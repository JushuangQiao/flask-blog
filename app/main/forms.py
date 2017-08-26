# coding=utf-8


from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp
from app.models.models import Role, User, Category


class NameForm(FlaskForm):
    name = StringField(u'姓名', validators=[DataRequired(message=u'姓名不能为空')])
    submit = SubmitField(u'提交')


class ProfileForm(FlaskForm):
    real_name = StringField(u'姓名', validators=[Length(0, 64)])
    age = IntegerField(u'年龄')
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')


class EditProfileForm(FlaskForm):
    real_name = StringField(u'姓名', validators=[Length(0, 64)])
    age = IntegerField(u'年龄')
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')


class EditAdminForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只能是字母、数字、点和下划线')])
    role = SelectField(u'角色', coerce=int)
    real_name = StringField(u'姓名', validators=[Length(0, 64)])
    location = StringField(u'地址', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经存在')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经存在')


class PostForm(FlaskForm):
    category = SelectField(u'文章类别', coerce=int)
    head = StringField(u'标题', validators=[DataRequired()])
    body = PageDownField(u'正文', validators=[DataRequired()])
    submit = SubmitField(u'发布')

    def __init__(self, *args, **kwargs):  # 定义下拉选择表
        FlaskForm.__init__(self, *args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField(u'提交')


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class SendMessageForm(FlaskForm):
    body = StringField(u'私信内容', validators=[Length(0, 256)])
    submit = SubmitField(u'发送')
