# coding=utf-8

from functools import wraps
from flask import g
from .errors import forbidden
from ..models.manager import UserManager


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not UserManager.can(g.current_user, permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
