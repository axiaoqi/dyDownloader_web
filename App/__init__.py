# 初始化文件：创建Flask应用

from flask import Flask
from .views import blue


def create_app():
    app = Flask(__name__)

    # 注册蓝图
    app.register_blueprint(blueprint=blue)

    return app

