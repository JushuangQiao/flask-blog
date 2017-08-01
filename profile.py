# coding=utf-8

import os
from werkzeug.contrib.profiler import ProfilerMiddleware
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
print 'starting'
app.run(debug=True, port=8889)
