#coding:utf-8
"""
main蓝本
"""
from flask import Blueprint

main = Blueprint('main',__name__)

# 导入包内模块
from . import views,errors
from ..models import Permission

# 导入上下文管理器
@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)