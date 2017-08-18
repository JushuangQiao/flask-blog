# coding = utf-8

from flask import render_template
from flask_login import login_required
from . import admin


@admin.route('/', methods=['GET', 'POST'])
@login_required
def edit():
    return render_template()
