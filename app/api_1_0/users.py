# coding=utf-8

from flask import jsonify, request, url_for
from . import api
from ..models.models import User, Post
from ..models.manager import UserManager, PostManager


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(UserManager.to_json(user))


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [PostManager.to_json(post) for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = UserManager.followed_posts(user).order_by(Post.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', page=page-1,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', page=page+1,
                       _external=True)
    return jsonify({
        'posts': [PostManager.to_json(post) for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
