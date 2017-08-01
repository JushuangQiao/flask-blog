# coding=utf-8

from flask import render_template, current_app
from flask_mail import Message
from setting.config import Config
from . import mail
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(Config.FLASKY_MAIL_SUBJECT_PREFIX+subject, sender=Config.FLASKY_MAIL_SENDER, recipients=[to])
    # 邮件内容会以文本和html两种格式呈现，而你能看到哪种格式取决于你的邮件客户端
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
