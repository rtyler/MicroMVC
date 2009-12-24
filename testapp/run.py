#!/usr/bin/env python

import sys

import MicroMVC

from testapp import controllers
from testapp import views

class TestApp(MicroMVC.Application):
    def controllers(self):
        return controllers
    def views(self):
        return views

def main():
    app = TestApp()
    return MicroMVC.run(app.run)

if __name__ == '__main__':
    sys.exit(main())

