#coding:utf-8
"""
配置项目
"""
import os
from sae.const import MYSQL_USER,MYSQL_PASS,MYSQL_HOST,MYSQL_PORT,MYSQL_DB

base_dir = os.path.dirname(__file__)
class Config():
    """定义基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you can not guess IT'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 10 # 连接池间隔时间
    SQLALCHEMY_ECHO = True


class DevelopingConfig(Config):
    """开发配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s'%(os.path.join(base_dir,'dev.db')) or \
                              os.environ.get('SQLALCHEMY_DATABASE_URI')
    QUESTION_COUNT = 4
    ANSWERS_PER_PAGE = 1
    QUESTIONS_PER_PAGE = 10

class ProductionConfig(Config):
    """生产配置"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s'%(os.path.join(base_dir,'pro.db')) or \
        os.path.get('SQLALCHEMY_DATABASE_URI')

class SaeProductionConfig(Config):
    """新浪SAE配置"""
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' \
    %(MYSQL_USER,MYSQL_PASS,
      MYSQL_HOST,int(MYSQL_PORT),MYSQL_DB)
class SaeDevelopingConfig(Config):
    """测试mysql数据库"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost:3306/microtest'


config = {
    'developing':DevelopingConfig,
    'production':ProductionConfig,
    'sae':SaeProductionConfig,
    'sae_test':SaeDevelopingConfig,
    'default':DevelopingConfig,

}


if __name__ == '__main__':
    print os.path.join(base_dir,'dev.db')