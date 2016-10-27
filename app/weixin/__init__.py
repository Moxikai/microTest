#coding:utf-8
"""
微信蓝本，处理微信公众平台相关请求
"""
from flask import Blueprint

weixin = Blueprint('weixin',__name__)

# 导入包内的模块
from . import errors,views