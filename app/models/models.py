# coding=utf-8

"""
数据表模型
"""
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from . import *
from .. import login_manager


class Permission:
    """
    权限
    """
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    """
    用户角色类型
    """
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<role {0}>'.format(self.name)


class Follow(db.Model):
    """
    用户关注
    """
    __tablename__ = 'follows'
    follower_id = Column(Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = Column(Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = Column(DateTime(), default=datetime.utcnow)

    def __init__(self, *args):
        self.follower_id = args[0]
        self.followed_id = args[1]


class User(UserMixin, db.Model):
    """
    用户模型
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True)
    password = Column(String(128))
    email = Column(String(64), unique=True, index=True)
    age = Column(Integer, nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    real_name = Column(String(64))
    location = Column(String(64))
    about_me = Column(Text())
    member_since = Column(DateTime(), default=datetime.utcnow)
    last_seen = Column(DateTime(), default=datetime.utcnow)
    posts = relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, username=None, password=None, email=None, age=None, role_id=None, real_name=None,
                 location=None, about_me=None, member_since=None, last_seen=None):
        self.username = username
        self.email = email
        self.age = age
        self.password = password
        self.role_id = Role.query.filter_by(default=True).first().id if role_id is None else int(role_id)
        self.real_name = real_name
        self.location = location
        self.about_me = about_me
        self.member_since = member_since
        self.last_seen = last_seen

    def __repr__(self):
        return '<user {0}>'.format(self.username)


class AnonymousUser(AnonymousUserMixin):
    """
    匿名用户
    """
    pass

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    """
    文章
    """
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    body = Column(Text)
    body_html = Column(Text)
    timestamp = Column(DateTime(), index=True, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'))
    comments = relationship('Comment', backref='post', lazy='dynamic')


class Comment(db.Model):
    """
    评论
    """
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    body = Column(Text)
    body_html = Column(Text)
    timestamp = Column(DateTime(), index=True, default=datetime.utcnow)
    disabled = Column(Boolean)
    author_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
