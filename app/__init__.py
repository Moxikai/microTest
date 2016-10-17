# coding:utf-8
"""
构造函数
"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment

from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()

def create_app(config_name):
    """工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    """实例化扩展"""
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    """此处注册蓝本"""
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app