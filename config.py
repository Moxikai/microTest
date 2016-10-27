#coding:utf-8
"""
配置项目
"""
import os
#from sae.const import MYSQL_USER,MYSQL_PASS,MYSQL_HOST,MYSQL_PORT,MYSQL_DB

base_dir = os.path.dirname(__file__)
class Config():
    """定义基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you can not guess IT'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 10 # 连接池间隔时间
    #SQLALCHEMY_ECHO = True
    QUESTIONS_COUNT_PER_TEST = 4 # 每次测试题目总数
    ANSWERS_PER_PAGE = 1
    QUESTIONS_PER_PAGE = 10 # 每页显示题目数量(题库管理界面)
    LOGIN_MODE = 0 # 登录模式,0为输入昵称,普通登录;1为从微信验证
    ADMINISTRATOR_MAIL = 'zhu-hero@qq.com'
    DATA_ADMIN_MAIL = '280004298@qq.com'


class DevelopingConfig(Config):
    """开发配置"""
    """服务器测试模式"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////PyProject/microTest/data.db' or \
                              'sqlite:///%s' % (os.path.join(base_dir, 'dev.db'))
    DEPLOY_MODE = 'public_test'
    CHANCE_DEFAULT_COUNT = 5  # 初始闯关机会
    CHEACK_PREV_PAGE = False  # 是否检查翻页动作
    DEFAULT_PASSWORD = '888888'


class ProductionConfig(Config):
    """生产配置"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:////PyProject/microTest/data.db' or \
        os.path.get('SQLALCHEMY_DATABASE_URI')
    CHANCE_DEFAULT_COUNT = 1  # 闯关机会，初始设置1

class SaeDevelopingConfig(Config):
    """测试本地mysql数据库"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:zhu098123@localhost:3306/app_microtest'


config = {
    'developing':DevelopingConfig,
    'production':ProductionConfig,
    'sae_test':SaeDevelopingConfig,
    'default':DevelopingConfig,
}


if __name__ == '__main__':
    print os.path.join(base_dir,'dev.db')
