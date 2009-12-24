#!/usr/bin/env python

import sys

import MicroMVC

class TestApp(MicroMVC.Application):
    pass

def main():
    app = TestApp()
    return MicroMVC.run(app.run)

if __name__ == '__main__':
    sys.exit(main())

