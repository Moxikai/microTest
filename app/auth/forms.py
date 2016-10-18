#coding:utf-8
"""
auth蓝本表单
"""
from flask_wtf import Form
from wtforms import SubmitField,StringField,IntegerField,BooleanField,PasswordField
from wtforms.validators import DataRequired,Email,Length

class LoginForm(Form):
    """登陆表单"""
    username_or_email = StringField('账号')
    password = PasswordField('密码',validators=[DataRequired()])
    remember_me = BooleanField('保持登陆')
    submit = SubmitField('登陆')
