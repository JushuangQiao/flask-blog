# coding=utf-8

import os
import logging
from logging.handlers import RotatingFileHandler

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Do not tell you'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    formatter = logging.Formatter(
        "[%(asctime)s][%(pathname)s:%(lineno)d][%(levelname)s] %(message)s")
    handler = RotatingFileHandler('./blog.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    @staticmethod
    def init_app(app):
        app.logger.addHandler(Config.handler)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://qiao:123456@localhost/f_blog'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://qiao:123456@localhost/test_blog'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://qiao:123456@localhost/blog'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
