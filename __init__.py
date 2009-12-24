#!/usr/bin/env python
import sys

from eventlet import api
from eventlet import wsgi
from eventlet import util
util.wrap_socket_with_coroutine_socket()

def run(app, host='', port=8081):
    try:
        wsgi.server(api.tcp_listener((host, port)), app)
    except keyboardinterrupt:
        print '>>> exiting cleanly...'
        return 0
    finally:
        return -1

