#coding:utf-8
"""
蓝本视图
"""
from flask import redirect,url_for,request,render_template,flash
from flask_login import login_user

from . import auth
from ..models import User
from .forms import LoginForm

@auth.route('/login',methods=['GET','POST'])
def login():
    """登陆视图，检查查询参数，提供从公众微信号进入用户静默登陆
    """
    form = LoginForm()
    # 这里检查链接查询参数，没有参数视作普通登陆

    if form.validate_on_submit():
        user_by_email = User.query.filter_by(email=form.username_or_email).first()
        user_by_username = User.query.filter_by(username=form.username_or_email).first()
        user = user_by_email if user_by_email else user_by_username
        if user is not None and user.verify_password(form.password.data):
            """用户存在且通过密码验证"""
            login_user(user,remember=form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户不存在或者密码错误')
    return render_template('auth/login.html',form=form)





