# coding=utf-8

"""
用户登录部分
"""

from flask import render_template, redirect, url_for, request, flash
from flask import current_app as app
from flask_login import logout_user, login_required, current_user
from . import auth
from ..models.manager import UserManager
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        UserManager.ping(current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    try:
        if form.validate_on_submit():
            email, password = form.email.data, form.password.data
            remember_me = form.remember_me.data
            user = UserManager.verify_password(email, password, remember_me)
            if user:
                return redirect(request.args.get('next') or url_for('main.home'))
            flash(u'用户名或密码错误')
        return render_template('auth/login.html', form=form)
    except Exception, e:
        app.logger.error('func: login error:{0}'.format(e))
        return render_template('auth/login.html', form=None)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已登出系统')
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    try:
        if form.validate_on_submit():
            UserManager.add_user(form)
            flash(u'注册成功')
            return redirect(url_for('auth.login'))
        return render_template('auth/register.html', form=form)
    except Exception, e:
        app.logger.error('func: register error:{0}'.format(e))
        return render_template('auth/register.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    try:
        if form.validate_on_submit():
            if current_user:
                UserManager.change_password(current_user, form)
                flash(u'密码已修改')
                return redirect(url_for('main.home'))
            else:
                flash(u'密码错误')
        return render_template('auth/change_password.html', form=form)
    except Exception, e:
        app.logger.error('func: change_password error:{0}'.format(e))
        return render_template('auth/change_password.html', form=None)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    try:
        if form.validate_on_submit():
            user1 = UserManager.get_user_by_name(form.username.data)
            user2 = UserManager.get_user_by_email(form.email.data)
            if not user1 or not user2:
                flash(u'用户名或邮箱不存在')
            if user1 != user2:
                flash(u'用户名和邮箱不一致')
            UserManager.change_password(user1, form)
            flash(u'密码重置成功')
            return redirect(request.args.get('next') or url_for('main.home'))
    except Exception, e:
        app.logger.error('func: reset_password error:{0}'.format(e))
        return render_template('auth/reset_password.html', form=form)
    return render_template('auth/reset_password.html', form=form)
