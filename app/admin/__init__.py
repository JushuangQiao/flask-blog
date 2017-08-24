from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views
from app.models.models import Permission


@admin.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
