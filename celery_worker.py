# coding=utf-8

from app import create_app
from celery import platforms


platforms.C_FORCE_ROOT = True   # 加上这一行
app = create_app('default')
app.app_context().push()
# start celery worker -A celery_worker.celery -l INFO  /
# celery worker -A celery_worker.celery --loglevel=info
