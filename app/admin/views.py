# coding=utf-8

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.models import Role, User, Post, Comment, Category
from app.models.manager import UserManager
from app.decorators import admin_required
from app import db
from . import admin
from .forms import AdminForm, UserForm, CategoryForm


@admin.route('/', methods=['GET', 'POST'])
@login_required
def edit():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter(User.role_id.in_([4, 5])).order_by(User.member_since.desc()).paginate(
        page, per_page=10, error_out=False)
    admins = pagination.items
    return render_template('admin/edit.html', admins=admins, pagination=pagination, page=page)


@admin.route('/admin2user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin2user(id):
    user = User.query.get_or_404(id)
    user.role = Role.query.filter_by(name='User').first()
    db.session.add(user)
    flash(u'已将"'+user.username+u' "降为普通用户')
    return redirect(url_for('admin.edit'))


@admin.route('/add-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def add_admin():
    form = AdminForm()
    if form.validate_on_submit():
        user = User(email=form.username.data+'@qiao.com', username=form.username.data,
                    password=form.password.data,
                    role_id=Role.query.filter_by(name='4').first().id)
        db.session.add(user)
        db.session.commit()
        flash(u'已添加" '+user.username+u' "为管理员')
        return redirect(url_for('main.edit'))
    return render_template('admin/add_admin.html', form=form)


@admin.route('/edit-user', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.member_since.desc()).paginate(page, per_page=10,
                                                                        error_out=False)
    users = pagination.items
    return render_template('admin/edit_user.html', users=users, pagination=pagination, page=page)


@admin.route('/delete-user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)

    posts = user.posts
    for post in posts:
        db.session.delete(post)
    comments = user.comments
    for comment in comments:
        db.session.delete(comment)
    messages = user.messages
    for message in messages:
        db.session.delete(message)
    web_pushes = user.web_pushes
    for web_push in web_pushes:
        db.session.delete(web_push)

    db.session.delete(user)
    flash(u'已将和" '+user.username+u' "相关的内容删除')
    return redirect(url_for('admin.edit_user'))


@admin.route('/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        UserManager.add_user(form)
        flash(u'已添加普通用户')
        return redirect(url_for('admin.edit_user'))
    return render_template('admin/add_user.html', form=form)


@admin.route('/edit-post', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=10,
                                                                     error_out=False)
    posts = pagination.items
    return render_template('admin/edit_post.html', posts=posts, pagination=pagination, page=page)


@admin.route('/post/delete/<int:id>')
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    for comment in post.comments:
        db.session.delete(comment)
    for web_push in post.webpushs:
        db.session.delete(web_push)
    flash(u'博客以及相关的评论、推送已删除')
    return redirect(url_for('main.edit_post'))


@admin.route('/edit-category', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category():
    categorys = Category.query.order_by(Category.id).all()
    return render_template('admin/edit_category.html', categorys=categorys)


@admin.route('/add-category', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('已添加" '+category.name+' "为新的分类')
        return redirect(url_for('.editcategory'))
    return render_template('admin/add_category.html',form=form)


@admin.route('/edit-comment')
@login_required
@admin_required
def edit_comment():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('admin/edit_comment.html', comments=comments,
                           pagination=pagination, page=page)


@admin.route('/delete-comment/<int:id>')
@login_required
@admin_required
def delete_comment_enable(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    return redirect(url_for('admin.edit_comment',
                            page=request.args.get('page', 1, type=int)))


@admin.route('/edit-comment/enable/<int:id>')
@login_required
@admin_required
def edit_comment_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('admin.edit_comment',
                            page=request.args.get('page', 1, type=int)), )


@admin.route('/edit-comment/disable/<int:id>')
@login_required
@admin_required
def edit_comment_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('admin.edit_comment',
                            page=request.args.get('page', 1, type=int)), )
