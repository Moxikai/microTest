#coding:utf-8
"""
构造函数
"""
from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views,errors,forms
