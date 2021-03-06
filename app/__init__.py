# coding:utf-8
"""
构造函数
"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    """工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    """实例化扩展"""
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    """此处注册蓝本"""
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix = '/auth')
    from .api_0_1_0 import api as api_0_1_0_blueprint
    app.register_blueprint(api_0_1_0_blueprint,url_frefix='/api/v0.1')

    return app