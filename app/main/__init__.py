#coding:utf-8
"""
main蓝本
"""
from flask import Blueprint

main = Blueprint('main',__name__)

# 导入包内模块
from . import views,errors