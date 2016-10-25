#coding:utf-8

from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,EqualTo,Regexp
from wtforms import ValidationError

from ..models import User

class LoginForm(Form):
    """登录表单"""
    email = StringField('Email',validators=[DataRequired(),
                                            Length(1,64),
                                            Email()])
    password = PasswordField('password',validators=[DataRequired()])
    remmember_me = BooleanField('记住我',default=True)
    submit = SubmitField('登录')

class RegisterForm(Form):
    """注册表单"""
    email = StringField('Email',validators=[DataRequired(),Length(1,64),
                                            Email()])
    username = StringField('用户名',validators=[DataRequired(),Length(1,64)])
    password = PasswordField('密码',validators=[DataRequired(),
                                              EqualTo('password2','前后密码必须一致')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self,field):
        """自定义验证email字段"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email已注册')

    def validate_username(self,field):
        """自定义用户名字段验证"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username已注册')
