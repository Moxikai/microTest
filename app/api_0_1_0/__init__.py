# coding:utf-8
"""
restful 分隔api，目前用于同步散落的问题库
"""
from flask import Blueprint

api = Blueprint('api',__name__)
from . import questions,users,errors

