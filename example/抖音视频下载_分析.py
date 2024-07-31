import re
from pathlib import Path

import requests
from jsonpath import jsonpath
from DrissionPage import ChromiumPage, ChromiumOptions  # 导入自动化模块

from App.utils.download_file import download_video


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
    txt_file_path = Path(Path.home() / 'Desktop' / f'{title}.txt')
    print(f'正在下载：{mp4_file_path}')
    download_video(download_url, mp4_file_path)
    with open(txt_file_path, 'w') as f:
        f.write(desc)
    return desc, mp4_file_path


def download(url):
    data = get_api_url(url)
    desc = parse_api_url_json_data(data)
    return desc


if __name__ == '__main__':
    url = input("请输入要下载的抖音链接：")
    s = download(url)
    print(s)


