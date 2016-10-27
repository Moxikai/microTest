# coding:utf-8
"""
微信蓝本视图，
验证服务器
"""
import hashlib

from flask import request,redirect,url_for,\
    session,abort,current_app
from . import weixin

@weixin.route('/confirm')
def confirm():
    """验证微信服务器"""
    # 获取查询参数
    signature = request.args.get('signature',None)
    timestamp = request.args.get('timestamp',None)
    nonce = request.args.get('nonce',None)
    echostr = request.args.get('echostr',None)
    # 从配置文件读取token
    token = current_app.config.get('WEIXIN_TOKEN')
    # signature,timestamp,nonce 组成列表，并排序
    if signature and timestamp and nonce and echostr:
        confirm_list = [token,timestamp,nonce]
        confirm_list.sort()
        # 列表转化为字符串
        confirm_str = ''.join(str(i) for i in confirm_list)
        # 生成sha1签名
        sha = hashlib.sha1()
        sha.update(confirm_str)
        sha1_sign = sha.hexdigest()
        if sha1_sign == signature:
            return echostr
        else:
            return False
    else:
        print '没有获取到微信参数'




