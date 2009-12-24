#!/usr/bin/env python
from __future__ import with_statement

import logging
import sys

from eventlet import api
from eventlet import greenio
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

class Application(object):
    ''' Subclassable WSGI application handle '''

    static_types = {
        'png' : 'image/png',
        'jpg' : 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif' : 'image/git',
        'css' : 'text/css',
        'js'  : 'text/javascript',
    }

    def controllers(self):
        return {}

    def _run(self, environ, start_response):
        path = environ['PATH_INFO']
        controller = self.controllers.get(path)

        if controller:
            klass, attr = controller
            controller = klass(start_response, **environ)
            result = [getattr(klass, attr)(controller, **controller.args) + '\r\n']
            return controller.finalize(result)

        ##
        ## If we don't have a static file, or somebody is giving me a crap URL
        ## I'm just going to bounce them back
        if '..' in path or not path.startswith('/static') \
                or not os.path.exists(os.getcwd() + path):
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['Not Found\r\n']

        segments = path.split('.')
        if static_types.get(segments[-1]):
            start_response('200 OK', [('Content-Type', static_types[segments[-1]])])
        else:
            start_response('200 OK', [('Content-Type', 'text/plain')])

        with open(os.getcwd() + path, 'r') as fd:
            return [fd.read()]


    def run(self, environ, start_response):
        try:
            return self._run(environ, start_response)
        except Exception, ex:
            logging.error('Serving a 500: %s' % ex)
            start_response('500 Server Error', [('Content-Type', 'text/plain')])
            return ['Server error\r\n']
