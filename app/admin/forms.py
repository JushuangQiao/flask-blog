# coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models.models import User, Category


class AdminForm(FlaskForm):
    username = StringField(u'用户名',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[a-zA-Z][a-zA-Z0-9._]*$', 0, u'用户名格式不正确')])
    password = PasswordField(u'密码',
                             validators=[DataRequired(),
                                         EqualTo('password2', message=u'输入密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'添加')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class UserForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[a-zA-Z][a-zA-Z0-9._]*$', 0, u'用户名格式不正确')])
    real_name = StringField(u'姓名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'密码',
                             validators=[DataRequired(),
                                         EqualTo('password2', message=u'输入密码不一致')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已存在')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class CategoryForm(FlaskForm):
    name = StringField(u'分类名称', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField(u'提交')

    def validate_username(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError(u'分类已存在')