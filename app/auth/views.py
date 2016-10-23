# coding:utf-8

from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,login_required,logout_user

from . import auth
from ..models import User
from .forms import LoginForm,RegisterForm
from .. import db

@auth.route('/login',methods=['GET','POST'])
def login():
    """登录,后续增加微信验证登录"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and \
                user.verify_password(form.password.data):
            login_user(user,form.remmember_me.data)
            return redirect(request.args.get('next') or url_for('main.welcome'))
        flash('账户或者密码错误')

    return render_template('auth/login.html',form=form)


@auth.route('/logout')
@login_required
def logout():
    """退出"""
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.welcome'))

@auth.route('/register',methods=['GET','POST'])
def register():
    """注册"""
    form = RegisterForm()
    if form.validate_on_submit():
        pass
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('稍后请登录')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html',form=form)

