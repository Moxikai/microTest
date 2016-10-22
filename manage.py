#coding:utf-8
"""
管理界面
"""
import os

from flask_migrate import Migrate,MigrateCommand
from flask_script import Shell,Manager

from app import db,create_app
from app.models import Answer,Question,User

 # 实例化app
app = create_app(os.environ.get('FLASK_CONFIG') or 'sae')
manager = Manager(app)
migrate = Migrate(app,db)

 # 注册shell命令
def make_shell_context():
    return dict(app=app,db=db,Answer=Answer,\
                Question=Question,User=User)

manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()


