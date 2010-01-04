#!/usr/bin/env python
from __future__ import with_statement

import cgi
import itertools
import logging
import os


class GenericControllerException(Exception):
    pass

code_map = {
        200 : '200 OK',
        301 : '301 Moved Permanently',
        302 : '302 Moved Temporarily',
        404 : '404 Not Found',
}

def action(**kwargs):
    def inner_f(method):
        if kwargs.get('paths'):
            method.paths = kwargs['paths']
        method.action = True
        return method
    return inner_f

class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read


GET  = 1
POST = 2

class BaseController(object):
    content_type = 'text/plain'
    _start = None
    environ = None
    code = 200
    posted = None
    method = GET
    args = None
    headers = None
    templates = None

    def __init__(self, start_response, **kwargs):
        self.environ = kwargs
        self.args = {}
        self.headers = []
        self.templates = {}
        ##
        ## Set all kwargs on myself, but make sure the names are getattr-able
        ## i.e. "wsgi.input" -> "wsgi_input"
        self.__dict__.update(dict(((k.replace('.', '_'), v) for k, v in kwargs.iteritems())))
        self._start = start_response

        if self.REQUEST_METHOD == 'POST':
            self.method = POST
            for k, v in dict(self.__process_form()).iteritems():
                if isinstance(v, cgi.MiniFieldStorage):
                    self.args[k] = v.value
                else:
                    self.args[k] = v
        else:
            self.method = GET
            if self.QUERY_STRING:
                self.args = dict(self.__iterquerystring())

    def finalize(self, output):
        logging.debug(self.headers)
        self._start(code_map[self.code], self.headers + [('Content-Type', self.content_type)])
        return output

    def __iterquerystring(self):
        if not self.REQUEST_METHOD == 'GET':
            yield (None, None)
        pieces = sorted((p.split('=') for p in self.QUERY_STRING.split('&')))
        ##
        ## This complexity exists so we handle duplicate keys correctly, i.e.
        ## `foo=bar&foo=baz` --> {'foo' : ['bar', 'baz']}
        for key, chunk in itertools.groupby(pieces, lambda p: p[0]):
            value = []
            for c in chunk:
                value.append(c[1])
            if len(value) == 1:
                value = value[0]
            yield (key, value)

    def __process_form(self):
        if not self.REQUEST_METHOD == 'POST':
            return None

        input = self.wsgi_input
        if hasattr(self, 'wsgi_post_form'):
            ## We've already got a processed form
            if self.wsgi_post_form[0] is input:
                return self.wsgi_post_form[2]

        # This must be done to avoid a bug in cgi.FieldStorage
        self.environ.setdefault('QUERY_STRING', '')
        fs = cgi.FieldStorage(fp=input, environ=self.environ, keep_blank_values=1)

        new_input = InputProcessed()
        post_form = (new_input, input, fs)
        self.wsgi_post_form = post_form
        self.wsgi_input = new_input
        return fs

    def render(self, name, **kwargs):
        kwargs.update({'controller' : self})
        template = self.templates.get(name)
        if not template:
            raise GenericControllerException('Could not find "%s" view' % name)
        return unicode(template(searchList=[kwargs]))

