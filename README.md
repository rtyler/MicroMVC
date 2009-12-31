About MicroMVC
==============

MicroMVC is a simplistic framework integrated with [eventlet](http://eventlet.net) 
and [Cheetah](http://cheetahtemplate.org) for writing quick web applications in
Python. It's partially modeled after ASP.NET MVC in the terminology and structure
of a given web application, but that's where the similarities end.


Getting Started
================
The structure [I](http://github.com/rtyler) use with **MicroMVC** is:

    myapp/
          run.py
          MyApp/
                __init__.py
                controllers/
                views/


The `run.py` file is there more for my own convenience and contains:

    #!/usr/bin/env python
    import sys
    import MicroMVC
    import MyApp

    def main():
        app = MyApp.MyApplication()
        return MicroMVC.run(app.run)

    if __name__ == '__main__':
        sys.exit(main())


Structuring your `MicroMVC.Application` subclass is quite easy as well:

    #!/usr/bin/env python
    import MicroMVC

    from MyApp import controllers
    from MyApp import views

    class MyApplication(MicroMVC.Application):
        controller_dir = 'MyApp.controllers'
        views_dir = 'MyApp.views'
        def controllers(self):
            return controllers
        def views(self):
            return views

It is worth noting that `controller_dir` and `views_dir` both exist to 
help MicroMVC properly import packages and their existence will be soon
obsoleted.

Writing a controller
--------------------
Controllers are where a lot of the work to set up a *view* is done, with MicroMVC
you can use controllers to determine the output content-type of your view as 
well as the URL routing for your view via the `MicroMVC.controller.action` decorator.
Below is a simple example controller:

    #!/usr/bin/env python
    from MicroMVC impor controller

    class home(controller.BaseController):
        content_type = 'text/html'
    
        @controller.action(paths=('/', '/index.html',))
        def index(self, **kwargs):
            return self.render('index', user='New User')
       
Walking through the controller from top to bottom, we are doing a few different 
things in a very small amount of code:

* Determine that all "actions" in the `home` controller will have the content-type of "text/html" (note: default is text/plain) 
* Map the `home.index` action to `http://host/`, `http://host/index.html`; additionally the action is mapped by default to `http://host/home/index`
* Render the view "index" (`MyApp/views/index.tmpl`) passing in the `$user` variable

Writing a view
---------------
Views are simply pre-compiled [Cheetah templates](http://cheetahtemplate.org)


TODO
======
* Parameterized paths for actions
* Models!
