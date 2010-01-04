#!/usr/bin/env python
from __future__ import with_statement

import logging
import os
import sys
import types

from eventlet import api
from eventlet import greenio
from eventlet import wsgi
from eventlet import util
util.wrap_socket_with_coroutine_socket()

def run(app, host='', port=8081):
    try:
        wsgi.server(api.tcp_listener((host, port)), app)
    except KeyboardInterrupt:
        print '>>> exiting cleanly...'
        return 0
    finally:
        return -1

class InvalidTypeException(Exception):
    pass

class Application(object):
    ''' Subclassable WSGI application handle '''
    _cached_controllers = None
    _cached_views = None
    controller_dir = 'controllers'
    views_dir = 'views'

    static_types = {
        'png' : 'image/png',
        'jpg' : 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif' : 'image/git',
        'css' : 'text/css',
        'js'  : 'text/javascript',
    }

    def controllers(self):
        ''' Override to return the package for your controllers '''
        return None

    def views(self):
        ''' Override to return the package for your views '''
        return None

    def _load_views(self):
        v_mod = self.views()
        if v_mod is None:
            yield

        if not isinstance(v_mod, types.ModuleType):
            raise InvalidTypeException('Expected views() to return a module')

        views_dir = os.path.dirname(v_mod.__file__)
        for v in os.listdir(views_dir):
            if not v.endswith('.py'):
                continue
            if v == '__init__.py':
                continue

            name = v.replace('.py', '')
            mod_name = '%s.%s' % (self.views_dir, name)
            __import__(mod_name)
            module = sys.modules.get(mod_name)
            klass = getattr(module, name, None)
            if not klass:
                continue
            yield (klass.__name__, klass)

    def _load_controllers(self):
        c_mod = self.controllers()
        if c_mod is None:
            yield

        if not isinstance(c_mod, types.ModuleType):
            raise InvalidTypeException('Expected controllers() to return a module')

        controller_dir = os.path.dirname(c_mod.__file__)
        for c in os.listdir(controller_dir):
            if not c.endswith('.py'):
                continue
            if c == '__init__.py':
                continue

            name = c.replace('.py', '')
            mod_name = '%s.%s' % (self.controller_dir, name)
            __import__(mod_name)
            module = sys.modules.get(mod_name)
            klass = getattr(module, name, None)

            if not klass:
                continue

            for attr in dir(klass):
                o = getattr(klass, attr)
                if not isinstance(o, (types.FunctionType, types.MethodType)):
                    continue
                if not getattr(o, 'action', False):
                    continue

                ## yield a default mapping for path-less actions
                ## yields up Controller/Action
                yield ('/%s/%s' % (klass.__name__, attr), (klass, attr))

                for path in getattr(o, 'paths', []):
                    yield (path, (klass, attr))

    def _controllers(self):
        if not self._cached_controllers:
            self._cached_controllers = dict(self._load_controllers())
        return self._cached_controllers

    def _views(self):
        if not self._cached_views:
            self._cached_views = dict(self._load_views())
        return self._cached_views

    def handle_404(self, environ, start_response):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']

    def _run(self, environ, start_response):
        path = environ['PATH_INFO']
        controller = self._controllers().get(path)
        views = self._views()

        if controller:
            klass, attr = controller
            controller = klass(start_response, **environ)
            controller.templates = views
            result = [getattr(klass, attr)(controller, **controller.args) + '\r\n']
            return controller.finalize(result)

        ##
        ## If we don't have a static file, or somebody is giving me a crap URL
        ## I'm just going to bounce them back
        if '..' in path or not path.startswith('/static') \
                or not os.path.exists(os.getcwd() + path):
            return self.handle_404(environ, start_response)

        segments = path.split('.')
        if self.static_types.get(segments[-1]):
            start_response('200 OK', [('Content-Type', self.static_types[segments[-1]])])
        else:
            start_response('200 OK', [('Content-Type', 'text/plain')])

        with open(os.getcwd() + path, 'r') as fd:
            return [fd.read()]

    def __call__(self, environ, start_response):
        return self.run(environ, start_response)

    def run(self, environ, start_response):
        try:
            return self._run(environ, start_response)
        except Exception, ex:
            logging.error('Serving a 500: %s' % ex)
            start_response('500 Server Error', [('Content-Type', 'text/plain')])
            return ['Server error\r\n']
