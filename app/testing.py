# coding=utf-8

from flask import jsonify
from app import app


@app.route('/hhh')
def hhh():
    try:
        app.logger.info('aaa')
        return jsonify(b='222')
    except Exception as e:
        app.logger.info(e)
        return jsonify(a='12')
