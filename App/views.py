import os
from flask import Blueprint, send_file, render_template, request
from .download_douyin_video import DownloadDouyinVideo


# 蓝图
blue = Blueprint('index', __name__)  #


@blue.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        douyinurl = request.form.get('douyinurl')
        downloader = DownloadDouyinVideo(url=douyinurl)
        file_name = downloader.download()

        current_path = os.getcwd()
        file_path = os.path.join(current_path, file_name)

        return send_file(file_path, as_attachment=True)


# 路由传参数
@blue.route('/download/<path:url>')
def download(url):
    downloader = DownloadDouyinVideo(url)
    file_name = downloader.download()

    current_path = os.getcwd()
    file_path = os.path.join(current_path, file_name)

    return send_file(file_path, as_attachment=True)








