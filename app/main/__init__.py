# coding=utf-8

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from app.models.manager import UserManager
from app.models.models import Permission


@main.app_context_processor
def inject_user_manager():
    return dict(UserManager=UserManager)


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

