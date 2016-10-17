#coding:utf-8
"""
main蓝本视图
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import redirect,url_for,render_template
from .. import db
from . import main

@main.route('/')
def index():
    """测试"""
    return render_template('index.html')