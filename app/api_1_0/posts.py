# coding=utf-8

from flask import jsonify, request, g, url_for
from .. import db
from ..models.models import Post, Permission
from ..models.manager import PostManager, UserManager
from . import api
from .decorators import permission_required
from .errors import forbidden
from .authentication import auth


@api.route('/posts/')
@auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [PostManager.to_json(post) for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(PostManager.to_json(post))


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    PostManager.add_post(head=request.form.get('head'), body=request.form.get('body'),
                         author=g.current_user)
    return jsonify({'success': True})


@api.route('/posts/<int:id>', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not UserManager.can(g.current_user, Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.title = request.form.get('head', post.head)
    post.body = request.form.get('body', post.body)
    db.session.add(post)
    return jsonify(PostManager.to_json(post))
