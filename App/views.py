import os
from flask import Blueprint, send_file, render_template, request
from .download_douyin_video import download_file


# 蓝图
blue = Blueprint('index', __name__)  #


@blue.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        douyinurl = request.form.get('douyinurl')
        desc, file_name = download_file(url=douyinurl)
        print(desc, file_name)
        return send_file(file_name, as_attachment=True)


# 路由传参数
@blue.route('/download/<path:url>')
def download(url):
    desc, file_name = download_file(url)
    return send_file(file_name, as_attachment=True)








