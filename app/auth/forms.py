# coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models.models import User


class LoginForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(message=u'邮箱不能为空'), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[DataRequired(u'密码不能为空')])
    remember_me = BooleanField(u'保存密码')
    submit = SubmitField(u'登录')


class RegistrationForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[a-zA-Z][a-zA-Z0-9._]*$', 0, u'用户名格式不正确')])
    real_name = StringField(u'姓名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message=u'输入密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已存在')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'当前密码', validators=[DataRequired()])
    password = PasswordField(u'新密码', validators=[DataRequired()])
    password2 = PasswordField(u'确认密码', validators=[DataRequired(), EqualTo('password', message=u'输入密码不一致')])
    submit = SubmitField(u'修改密码')


class ResetPasswordForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message=u'输入密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'重置密码')
