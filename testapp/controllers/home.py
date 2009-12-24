#!/usr/bin/env python

from MicroMVC import controller

from testapp import views

class home(controller.BaseController):
    content_type = 'text/html'

    @controller.action(paths=('/', '/Default.aspx'))
    def index(self, **kwargs):
        return self.render('index')

    @controller.action(paths=('/test',))
    def testy(self):
        return 'Feeling testy?'

    @controller.action()
    def home(self, **kwargs):
        return 'Fail'
