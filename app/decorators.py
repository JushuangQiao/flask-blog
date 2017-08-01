# coding=utf-8

from functools import wraps
from flask import abort
from flask_login import current_user
from .models.models import Permission
from .models.manager import UserManager


def permission_required(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not UserManager.can(current_user, permissions):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
