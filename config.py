#coding:utf-8
"""
配置项目
"""
import os

base_dir = os.path.dirname(__file__)
class Config():
    """定义基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you can not guess IT'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopingConfig(Config):
    """开发配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s'%(os.path.join(base_dir,'dev.db')) or \
                              os.environ.get('SQLALCHEMY_DATABASE_URI')
    QUESTION_COUNT = 4
    ANSWERS_PER_PAGE = 1

class ProductionConfig(Config):
    """生产配置"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s'%(os.path.join(base_dir,'pro.db')) or \
        os.path.get('SQLALCHEMY_DATABASE_URI')

config = {
    'developing':DevelopingConfig,
    'production':ProductionConfig,
    'default':DevelopingConfig
}


if __name__ == '__main__':
    print base_dir