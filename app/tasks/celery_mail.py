# coding=utf-8

from app import celery, mail, create_app
from app.models.models import User, Post, WebPush


@celery.task
def send_async_email(msg):
    app = create_app('default')
    with app.app_context():
        mail.send(msg)


@celery.task
def send_async_web_push(username, post_id):
    app = create_app('default')
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        post = Post.query.get(post_id)
        followers = user.followers
        for follower in followers:
            if follower.follower != user:
                webpush = WebPush(sendto=follower.follower, author=user, post_id=post.id)

