import re
import requests
import os
import json

from tqdm import tqdm
from datetime import datetime


def download_video(url, name):
    response = requests.get(url, stream=True)
    if not os.path.exists(name):
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
            with open(name, 'wb') as file:
                for chunk in response.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    file.write(chunk)
            progress_bar.close()
            return True
        else:
            return False


class DownloadDouyinVideo(object):
    """
    第一步：获取视频的item_ids
    第二步：获取视频的信息，及下载地址（重定向一下）
    第三步：下载保存视频
    """
    def __init__(self, url):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"}

    def redirect(self, need_redirect_url):
        response = requests.get(url=need_redirect_url, headers=self.headers, allow_redirects=False)
        redirect_url = response.headers['location']
        return redirect_url

    def get_item_ids(self):
        # 短地址或者口令
        if 'https://www.douyin.com/video/' not in self.url:
            short_url = 'https://v.douyin.com/' + self.url.split('https://v.douyin.com/')[-1]
            self.url = self.redirect(short_url)
            # 获取id
            item_ids = re.findall(f"{'/video/'}(.*?){'/?region='}", self.url)[0][:-2]
        else:
            item_ids = self.url.split('/video/')[1]
        return item_ids

    def get_file_data(self, ids):
        json_url = f"https://m.douyin.com/web/api/v2/aweme/iteminfo/?a_bogus=&item_ids={ids}"
        response = requests.get(url=json_url, headers=self.headers)
        data = json.loads(response.text)['item_list'][0]

        desc = data['desc']  # 描述
        create_time = datetime.fromtimestamp(data['create_time']).strftime('%Y-%m-%d')  # 发布时间,这里取日期
        author = data['author']['nickname']  # 作者

        # 获取下载链接
        ___file_url = data['video']['play_addr']['url_list'][0]
        # 去水印
        __file_url = ___file_url.replace('/playwm/', '/play/')
        # 720p改成1080p
        _file_url = __file_url.replace('ratio=720p', 'ratio=1080p')
        # 重定向下载链接
        file_url = self.redirect(_file_url)

        # 文件名
        file_name = f'{author}_{create_time}_{desc}.mp4'

        return file_name, file_url

    def download(self):
        item_ids = self.get_item_ids()
        file_name, file_url = self.get_file_data(ids=item_ids)
        download_video(url=file_url, name=file_name)

        return file_name
