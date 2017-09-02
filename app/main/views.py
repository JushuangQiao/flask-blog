# coding=utf-8

"""
主要的接口
"""

from flask import render_template, url_for, redirect, request, abort, g
from flask import current_app as app
from flask import make_response, flash
from flask_login import login_required, current_user
from . import main
from forms import EditProfileForm, EditAdminForm, PostForm, CommentForm, SendMessageForm
from app.models import db
from app.models.models import User, Permission, Post, Comment, Category, Message, WebPush
from app.decorators import admin_required, permission_required
from app.models.manager import UserManager, PostManager, CommentManager
from app.tasks.celery_mail import send_async_web_push


@main.route('/blog', methods=['GET', 'POST'])
def blog():
    form = PostForm()
    if current_user.is_anonymous:
        return redirect(url_for('main.show_all'))
    user = User.query.filter_by(username=current_user.username).first_or_404()
    if UserManager.can(current_user, Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = PostManager.add_post(head=form.head.data, body=form.body.data, author=current_user,
                                    category=Category.query.get(form.category.data))
        username = current_user.username
        post_id = post.id
        send_async_web_push.delay(username=username, post_id=post_id)
        flash(u"博客已发布")
        return redirect(url_for('main.home'))
    return render_template('main/write_blog.html', user=user, form=form)


@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
    user = User()
    message = Message()
    category = Category()
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = UserManager.followed_posts(current_user)
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items  # 分页显示

    return render_template('main/home.html', posts=posts, user=user, message=message,
                           category=category, show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
@login_required
def user_detail(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    try:
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.filter_by(author_id=user.id).order_by(
            Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
        posts = pagination.items
        return render_template('main/user_detail.html', user=user,
                               posts=posts, pagination=pagination)
    except Exception, e:
        app.logger.error('func: detail failed:{0}'.format(e))
        abort(500)


@main.route('/user/<username>/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()
    try:
        if form.validate_on_submit():
            UserManager.edit_profile(current_user, form)
            flash(u'您的资料已更改')
            return redirect(url_for('main.user_detail', username=username))
        return render_template('main/edit_profile.html', form=UserManager.get_profile(
            current_user, form))
    except Exception, e:
        app.logger.error('func:edit_profile error:{0}'.format(e))
        return render_template('main/edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditAdminForm(user=user)
    try:
        if form.validate_on_submit():
            UserManager.edit_profile_admin(user, form)
            flash(u'资料已更改')
            return redirect(url_for('main.user_detail', username=user.username))
        form = UserManager.get_profile_admin(user, form)
        return render_template('main/edit_profile.html', form=form, user=user)
    except Exception, e:
        app.logger.error('func: edit_profile_admin error:{0}'.format(e))
        return render_template('main/edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    hot_post = Post.hotpost()
    posts = Post.query.get_or_404(id)
    form = CommentForm()
    posts.visits += 1
    try:
        if form.validate_on_submit():
            CommentManager.add_comment(body=form.body.data, post=posts, author=current_user)
            flash(u'你的评论已提交.')
            return redirect(url_for('main.post', id=posts.id, page=-1))
        page = request.args.get('page', 1, type=int)
        if page == -1:
            page = (posts.comments.count() - 1) / 10 + 1
        pagination = posts.comments.order_by(Comment.timestamp.asc()).paginate(
            page, per_page=10, error_out=False)
        comments = pagination.items
        return render_template('main/post.html', posts=[posts], form=form, hot_post=hot_post,
                               pagination=pagination, comments=comments)
    except Exception, e:
        app.logger.error('func: post error:{0}'.format(e))
        abort(500)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not UserManager.can(current_user, Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.head = form.head.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.add(post)
        return redirect(url_for('main.post', id=post.id))
    form.head.data = post.head
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('main/edit_post.html', form=form)


@main.route('/delete/<int:id>', methods=['GET', 'POST'])
def del_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not UserManager.can(current_user, Permission.ADMINISTER):
        abort(403)
    try:
        ret = PostManager.del_post(id)
        flash(u'删除成功') if ret else flash(u'删除失败')
    except Exception as e:
        app.logger.error('del_post failed: {0}'.format(e))
    finally:
        return redirect(url_for('main.home'))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('main.user_detail', username=username))
    if UserManager.is_following(current_user, user):
        return redirect(url_for('main.user_detail', username=username))
    UserManager.follow(current_user, user)
    return redirect(url_for('main.user_detail', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('main.user_detail', username=username))
    if not UserManager.is_following(current_user, user):
        return redirect(url_for('main.user_detail', username=username))
    UserManager.unfollow(current_user, user)
    return redirect(url_for('main.user_detail', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('main.home'))
    if user == current_user:
        title = u'我的粉丝'
    else:
        title = user.real_name + u'的粉丝'
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=10, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('main/followers.html', user=user, title=title,
                           endpoint='main.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('main.home'))
    if user == current_user:
        title = u'我的关注'
    else:
        title = user.real_name + u'的关注'
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=10, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('main/followers.html', user=user, title=title,
                           endpoint='main.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
# @login_required
def show_all():
    if current_user.is_anonymous:
        page = request.args.get('page', 1, type=int)
        query = Post.query
        pagination = query.order_by(Post.timestamp.desc()).paginate(page,
                                                                    per_page=10, error_out=False)
        posts = pagination.items
        return render_template('main/all_posts.html', posts=posts, pagination=pagination)
    else:
        resp = make_response(redirect(url_for('main.home')))
        resp.set_cookie('show_followed', '', max_age=30*24*60*60)
        return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.home')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('main/moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/user/<username>/comments')
def user_comments(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('main/user_comments.html', comments=comments, user=user,
                           pagination=pagination, page=page)


@main.route('/delete_user_comments/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def delete_user_comments(id):
    comment = Comment.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    db.session.delete(comment)
    flash(u"评论已删除")
    return redirect(url_for('main.user_comments', username=current_user.username, page=page))


@main.route('/star/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def star(id):
    post = Post.query.get_or_404(id)
    if current_user.staring(post):
        flash(u'你已经收藏了这篇文章')
        return redirect(url_for('main.post', id=post.id))
    current_user.star(post)
    flash(u'收藏完成')
    return redirect(url_for('main.post', id=post.id))


@main.route('/unstar/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unstar(id):
    post = Post.query.get_or_404(id)
    if not current_user.staring(post):
        flash(u'你没有收藏这篇文章')
        return redirect(url_for('main.post', id=post.id))
    current_user.unstar(post)
    flash(u'你不再收藏这篇旷世奇文了，太可惜了，你与大牛失之交臂')
    return redirect(url_for('main.post', id=post.id))


@main.route('/delete-star/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def delete_star(id):
    post = Post.query.get_or_404(id)
    if not current_user.staring(post):
        flash(u'你没有收藏这篇文章')
        return redirect(url_for('main.star_posts', username=current_user.username))
    current_user.unstar(post)
    flash(u'你不再收藏这篇旷世奇文了，太可惜了，你与大牛失之交臂')
    return redirect(url_for('main.star_posts', username=current_user.username))


@main.route('/user/<username>/star-posts')
def star_posts(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type=int)
    posts = user.star_posts
    return render_template('main/user_star_posts.html', user=user, title=u"收藏的文章",
                           posts=posts)


@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('main/about.html')


@main.route('/show-message')
@login_required
@permission_required(Permission.COMMENT)
def show_message():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.order_by(Message.timestamp.desc()).filter_by(
        sendto=current_user).paginate(page, per_page=10, error_out=False)
    messages = pagination.items
    return render_template('main/show_message.html', messages=messages,
                           pagination=pagination, page=page)


@main.route('/send-message/<username>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.COMMENT)
def send_message(username):
    user = User.query.filter_by(username=username).first()
    form = SendMessageForm()
    if form.validate_on_submit():
        message = Message(body=form.body.data, author=current_user, sendto=user)
        db.session.add(message)
        db.session.commit()
        flash(u'私信发送成功')
        return redirect(url_for('main.user_detail', username=username))

    return render_template('main/send_message.html', form=form)


@main.route('/show-message/unconfirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def show_message_unconfirmed(id):
    message = Message.query.get_or_404(id)
    message.confirmed = True
    db.session.add(message)
    return redirect(url_for('main.show_message', page=request.args.get('page', 1, type=int)))


@main.route('/show-message/confirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def show_message_confirmed(id):
    message = Message.query.get_or_404(id)
    message.confirmed = False
    db.session.add(message)
    return redirect(url_for('main.show_message', page=request.args.get('page', 1, type=int)))


@main.route('/show-message/delete/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def message_delete(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    flash(u'私信删除成功')
    return redirect(url_for('main.show_message', page=request.args.get('page', 1, type=int)))


@main.route('/show-notice')
@login_required
@permission_required(Permission.COMMENT)
def show_notice():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('main/show_notice.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/show-notice/unconfirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def show_notice_unconfirmed(id):
    comment = Comment.query.get_or_404(id)
    comment.confirmed = True
    db.session.add(comment)
    return redirect(url_for('main.show_notice', page=request.args.get('page', 1, type=int)))


@main.route('/show-notice/confirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def show_notice_confirmed(id):
    comment = Comment.query.get_or_404(id)
    comment.confirmed = False
    db.session.add(comment)
    return redirect(url_for('main.show_notice', page=request.args.get('page', 1, type=int)))


@main.route('/<username>/show-web-push')
@login_required
@permission_required(Permission.COMMENT)
def show_web_push(username):
    page = request.args.get('page', 1, type=int)
    pagination = WebPush.query.order_by(WebPush.timestamp.desc()).filter_by(
        sendto=current_user).paginate(page, per_page=10, error_out=False)
    web_pushes = pagination.items
    return render_template('main/web_push.html', web_pushes=web_pushes,
                           pagination=pagination, page=page)


@main.route('/web-push/unconfirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def web_push_unconfirmed(id):
    web_push = WebPush.query.get_or_404(id)
    web_push.confirmed = True
    db.session.add(web_push)
    return redirect(url_for('main.show_web_push', page=request.args.get('page', 1, type=int),
                            username=request.args.get('username')))


@main.route('/web-push/confirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def web_push_confirmed(id):
    web_push = WebPush.query.get_or_404(id)
    web_push.confirmed = False
    db.session.add(web_push)
    return redirect(url_for('main.show_web_push', page=request.args.get('page', 1, type=int),
                            username=request.args.get('username')))


@main.route('/show-web-push/delete/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def web_push_delete(id):
    web_push = WebPush.query.get_or_404(id)
    db.session.delete(web_push)
    flash(u'消息删除成功')
    return redirect(url_for('main.show_web_push', page=request.args.get('page', 1, type=int),
                            username=request.args.get('username')))


@main.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('main.home'))
    return redirect(url_for('main.search_results', query=g.search_form.search.data))


@main.route('/search_results/<query>')
def search_results(query):
    posts = Post.query.filter(Post.head.like('%'+query+'%')).all()
    return render_template('main/search_results.html', query=query, posts=posts)


@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('main/category.html', category=category, posts=posts,
                           pagination=pagination)

