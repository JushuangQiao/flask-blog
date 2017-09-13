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
    用户角色
    """
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')
    home = db.Column(db.String(64), unique=True)

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


class WebPush(db.Model):
    # 网站推送
    __tablename__ = 'web_pushes'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime,  default=datetime.now)
    confirmed = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sendto_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return '<WebPush %r  push_time %r >'.format(self.sendto, self.timestamp)


class Message(db.Model):
    # 私信
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,  default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sendto_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Message %r  from %r sent to %r>'.format(self.body, self.author.username,
                                                         self.sendto.username)


class Star(db.Model):
    # 收藏
    __tablename__ = 'stars'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)


class User(UserMixin, db.Model):
    # 用户
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True)
    password = Column(String(128))
    email = Column(String(64), unique=True, index=True)
    age = Column(Integer, nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    real_name = Column(String(64))
    location = Column(String(64))
    avatar_hash = db.Column(db.String(32))
    about_me = Column(Text())
    member_since = Column(DateTime(), default=datetime.utcnow)
    last_seen = Column(DateTime(), default=datetime.utcnow)
    posts = relationship('Post', backref='author', lazy='dynamic')
    star_posts = db.relationship('Post', secondary='stars',
                                 backref=db.backref('stared', lazy='joined'), lazy='joined')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic', cascade='all, delete-orphan')
    commented = db.relationship('Comment', backref='sendto', lazy='dynamic',
                                primaryjoin='Comment.sendto_id==User.id')

    comments = db.relationship('Comment', backref='author', lazy='dynamic',
                               primaryjoin='Comment.author_id==User.id')

    messages = db.relationship('Message', backref='author', lazy='dynamic',
                               primaryjoin='Message.author_id==User.id')

    messageds = db.relationship('Message', backref='sendto', lazy='dynamic',
                                primaryjoin='Message.sendto_id==User.id')

    web_pushes = db.relationship('WebPush', backref='sendto', lazy='dynamic',
                                 primaryjoin='WebPush.sendto_id==User.id')

    web_sents = db.relationship('WebPush', backref='author', lazy='dynamic',
                                primaryjoin='WebPush.author_id==User.id')

    def __init__(self, username=None, password=None, email=None, age=None, role_id=None,
                 real_name=None, location=None, about_me=None, member_since=None, last_seen=None):
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

    # 订阅
    def unread_web_pushes(self):
        maxi = self.web_pushes.count()
        total = 0
        for i in range(0, maxi):
            if not self.web_pushes[i].confirmed:
                total = total + 1
        return total

    def last_web_push(self):
        if self.web_pushes.count() > 0:
            return self.web_pushes[-1]

    def gravatar(self, size=100, default='identicon', rating='g'):
        from flask import request
        import hashlib
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    # 收藏/取消收藏
    def star(self, post):
        if not self.staring(post):
            s = Star(user_id=self.id, post_id=post.id)
            db.session.add(s)
            db.session.commit()

    def unstar(self, post):
        if self.staring(post):
            uns = Star.query.filter_by(user_id=self.id, post_id=post.id).first()
            db.session.delete(uns)
            db.session.commit()

    def staring(self, post):
        if Star.query.filter_by(user_id=self.id, post_id=post.id).first():
            return True
        else:
            return False

    def star_timestamp(self,post):
        star = Star.query.filter_by(user_id=self.id, post_id=post.id).first()
        return star.timestamp

    # 私信
    def unread_messages(self):
        maxi = self.messageds.count()
        total = 0
        for i in range(0, maxi):
            if not self.messageds[i].confirmed:
                total = total+1
        return total

    def last_message(self):
        last = self.messageds[-1]
        return last

    def last_message_form(self):
        last_form = self.messageds[-1].author
        return last_form

    # 计算被评论数
    def unread_comments(self):
        total = 0
        for comment in self.commented:
            if not comment.confirmed:
                total = total+1
        return total

    def last_comment(self):
        return self.commented[-1]

    def last_comment_form(self):
        return self.commented[-1].author

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)


class AnonymousUser(AnonymousUserMixin):
    """
    匿名用户
    """
    pass

login_manager.anonymous_user = AnonymousUser


class Category(db.Model):
    __tablename__ = 'categorys'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    @staticmethod
    def insert_categorys():
        categorylist = ["Python", "Web", "Linux", "c/c++", u"数据库", u"前端", u"杂记"]
        for category in categorylist:
            postcategory = Category.query.filter_by(name=category).first()
            if postcategory is None:
                postcategory = Category(name=category)
                db.session.add(postcategory)
        db.session.commit()

    def __repr__(self):
        return '<Category %r>' % self.name


class Post(db.Model):
    # 文章
    __tablename__ = 'posts'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    head = Column(String(256))
    body = Column(Text)
    body_html = Column(Text)
    timestamp = Column(DateTime(), index=True, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'))
    comments = relationship('Comment', backref='post', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    visits = db.Column(db.Integer, nullable=False, default=int(10))
    web_pushes = db.relationship('WebPush', backref='post', lazy='dynamic')

    @staticmethod
    def hotpost():  # 热门文章排序，取前10
        posts = Post.query.all()

        def byvisits(p):
            return p.visits

        posts_byvisits = sorted(posts, key=byvisits, reverse=True)
        return posts_byvisits[0:10]


class Comment(db.Model):
    """
    评论
    """
    __tablename__ = 'comments'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    body = Column(Text)
    body_html = Column(Text)
    timestamp = Column(DateTime(), index=True, default=datetime.utcnow)
    disabled = Column(Boolean)
    author_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    sendto_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    confirmed = db.Column(db.Boolean, default=False)


