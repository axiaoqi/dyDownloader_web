import re
from pathlib import Path

import requests
from jsonpath import jsonpath
from DrissionPage import ChromiumPage, ChromiumOptions  # 导入自动化模块

from App.utils.download_file import download_video


def file_name_less_255(file_name):
    # 判断标题字节数
    max_bytes_num = 255
    i = 0
    mp4_num = 4

    # 文件标题过长，缩减到255字节长度
    if len(file_name.encode()) > max_bytes_num:
        cut_file_name_bytes = file_name.encode('utf-8')
        while True:
            try:
                cut_file_name_tmp = cut_file_name_bytes[:max_bytes_num-mp4_num-i]
                file_name = cut_file_name_tmp.decode('utf-8') + '.mp4'
                break
            except Exception as e:
                print("文件名过长，正在重试...%s", e)
            i += 1

    return file_name



# class DownloadDouyinVideo(object):
#     """
#     第一步：获取视频的item_ids
#     第二步：获取视频的信息，及下载地址（重定向一下）
#     第三步：下载保存视频
#     """
#     def __init__(self, url):
#         self.url = url
#         self.headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"}
#
#     def redirect(self, need_redirect_url):
#         response = requests.get(url=need_redirect_url, headers=self.headers, allow_redirects=False)
#         redirect_url = response.headers['location']
#         return redirect_url
#
#     def get_item_ids(self):
#         # 短地址或者口令
#         if 'https://www.douyin.com/video/' not in self.url:
#             short_url = 'https://v.douyin.com/' + self.url.split('https://v.douyin.com/')[-1]
#             self.url = self.redirect(short_url)
#             # 获取id
#             item_ids = re.findall(f"{'/video/'}(.*?){'/?region='}", self.url)[0][:-2]
#         else:
#             item_ids = self.url.split('/video/')[1]
#         return item_ids
#
#     def get_file_data(self, ids):
#         json_url = f"https://m.douyin.com/web/api/v2/aweme/iteminfo/?a_bogus=&item_ids={ids}"
#         response = requests.get(url=json_url, headers=self.headers)
#         data = json.loads(response.text)['item_list'][0]
#
#         desc = data['desc'].replace('\n', '')  # 描述
#         create_time = datetime.fromtimestamp(data['create_time']).strftime('%Y-%m-%d')  # 发布时间,这里取日期
#         author = data['author']['nickname']  # 作者
#
#         # 获取下载链接
#         ___file_url = data['video']['play_addr']['url_list'][0]
#         # 去水印
#         __file_url = ___file_url.replace('/playwm/', '/play/')
#         # 720p改成1080p
#         _file_url = __file_url.replace('ratio=720p', 'ratio=1080p')
#         # 重定向下载链接
#         file_url = self.redirect(_file_url)
#
#         # 获取点赞，评论，收藏，分享数量
#         # digg_count：点赞
#         # comment_count：评论
#         # collect_count：收藏
#         # share_count：分享
#         statistics = data['statistics']
#         file_status = f"赞{statistics['digg_count']}_评{statistics['comment_count']}_藏{statistics['collect_count']}_享{statistics['share_count']}"
#
#         # 文件名
#         file_name = f'{author}_{create_time}_{file_status}_{desc}.mp4'
#
#         # 文件名超过255字节处理
#         file_name = file_name_less_255(file_name)
#
#         return file_name, file_url
#
#     def download(self):
#         item_ids = self.get_item_ids()
#         file_name, file_url = self.get_file_data(ids=item_ids)
#         download_video(url=file_url, name=file_name)
#
#         return file_name


def redirect(need_redirect_url):
    """
    抖音短连接重定向
    """
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"}
    response = requests.get(url=need_redirect_url, headers=headers, allow_redirects=False)
    redirect_url = response.headers['location']
    return redirect_url


def get_item_real_url(url):
    """
    抖音分享的短连接转为正常的带id的链接
    """
    # 短地址或者口令
    if 'https://www.douyin.com/video/' not in url:
        # 获取真实短连接
        short_url = 'https://v.douyin.com/' + url.split('https://v.douyin.com/')[-1]
        # 短连接重定向
        url = redirect(short_url)
        # 获取id
        item_ids = re.findall(f"{'/video/'}(.*?){'/?region='}", url)[0][:-2]
        # 拼接url
        url = 'https://www.douyin.com/video/' + str(item_ids)
    return url


def get_api_url(url):
    url = get_item_real_url(url)
    co = ChromiumOptions()
    co.headless()
    # 打开浏览器
    dp = ChromiumPage(co)
    # 监听数据包
    dp.listen.start('aweme/v1/web/aweme/detail/')
    # 访问网站
    dp.get(url)
    # 等待数据包加载
    resp = dp.listen.wait()

    # 获取api_url的response
    api_url_json_data = resp.response.body

    return api_url_json_data


def parse_api_url_json_data(data):
    """
    这个api包含数据很详细
    """
    # base_url = 'https://www.douyin.com/aweme/v1/web/aweme/detail/'
    # params = {
    #     'device_platform': 'webapp',
    #     'aid': 6383,
    #     'channel': 'channel_pc_web',
    #     'aweme_id': 7383142996054674727,
    #     'update_version_code': 170400,
    #     'pc_client_type': 1,
    #     'version_code': 190500,
    #     'version_name': '19.5.0',
    #     'cookie_enabled': 'true',
    #     'screen_width': 1280,
    #     'screen_height': 720,
    #     'browser_language': 'zh-CN',
    #     'browser_platform': 'Win32',
    #     'browser_name': 'Chrome',
    #     'browser_version': '127.0.0.0',
    #     'browser_online': 'true',
    #     'engine_name': 'Blink',
    #     'engine_version': '127.0.0.0',
    #     'os_name': 'Windows',
    #     'os_version': 10,
    #     'cpu_core_num': 8,
    #     'device_memory': 8,
    #     'platform': 'PC',
    #     'downlink': 10,
    #     'effective_type': '4g',
    #     'round_trip_time': 100,
    #     'webid': 7345838841952044553,
    #     'verifyFp': 'verify_lycb5zj3_K39GGHOi_iP0l_44JL_8jHh_wwxYe7gc5d5Q',
    #     'fp': 'verify_lycb5zj3_K39GGHOi_iP0l_44JL_8jHh_wwxYe7gc5d5Q',
    #     'msToken': 'zi6QVMoVjuZ2wW9HNRzRuNrUH6FZuean1cFtwBQjRFUaTCYA2XkFSBb740ZpSyc6aUULvzKujGa7SXnfTE99BR1ryUHA3xJOVaNdPVYDTvxnTiqYoM8=',
    #     'a_bogus': 'd6WhQdwvdE6kDfyh5RQLfY3q6WP3YDu10trEMD2fcnfrr639HMOE9exoL3tvkvyjN4/kIb6jy4hcOpaMi5c7A3v378DKWooh-g00t-P2so0j5Z4aeju/ntmF-vJ1SaB05JV3iQ4hy7QSKuRplnAJ5k1cthMea6m=',
    # }

    resp_json = data

    download_url = jsonpath(resp_json, '$..play_addr_h264.url_list')[0][2]
    author_name = jsonpath(resp_json, '$..nickname')[0]
    title = jsonpath(resp_json, '$..caption')[0]
    seo_info = jsonpath(resp_json, '$..seo_info.ocr_content')[0]

    # 作品数据
    dianzan = jsonpath(resp_json, '$..digg_count')[0]
    shoucang = jsonpath(resp_json, '$..collect_count')[0]
    pinglun = jsonpath(resp_json, '$..comment_count')[0]
    zhuanfa = jsonpath(resp_json, '$..share_count')[0]
    douzaisou = jsonpath(resp_json, '$..word')[0]

    desc = (f'作者：{author_name}\n'
            f'作品名称：{title}\n'
            f'点赞：{dianzan}，收藏：{shoucang}，评论：{pinglun}，转发：{zhuanfa}\n'
            f'大家都在搜：{douzaisou}\n'
            f'SEO信息：{seo_info}\n'
            )
    mp4_file_path = Path(Path.home() / 'Desktop' / f'{title}.mp4')
    mp4_file_path = file_name_less_255(str(mp4_file_path))

    txt_file_path = Path(Path.home() / 'Desktop' / f'{title}.txt')
    print(f'正在下载：{mp4_file_path}')
    download_video(download_url, mp4_file_path)
    with open(txt_file_path, 'w') as f:
        f.write(desc)
    return desc, mp4_file_path


def download_file(url):
    data = get_api_url(url)
    desc, mp4_file_path = parse_api_url_json_data(data)
    return desc, mp4_file_path


if __name__ == '__main__':
    url = input("请输入要下载的抖音链接：")
    desc, mp4_file_path = download_file(url)
    print(desc)


