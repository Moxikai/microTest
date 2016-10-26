#coding:utf-8
"""
处理API蓝本错误
"""
from flask import jsonify
from . import api
from app.exceptions import ValidationError

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])