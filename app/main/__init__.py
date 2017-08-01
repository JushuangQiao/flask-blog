# coding=utf-8

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models.models import Permission
from ..models.manager import UserManager


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.app_context_processor
def inject_user_manager():
    return dict(UserManager=UserManager)
