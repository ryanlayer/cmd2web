#!/usr/bin/python
import sys,os
import logging
activate_this = '/home/rohit/Documents/Academics/sem4/IndependentStudy/forkedrepo/cmd2web/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/rohit/Documents/Academics/sem4/IndependentStudy/forkedrepo/cmd2web/src")

from server import app as application
application.secret_key = 'Add your secret key'

# def application(environ, start_response):
#     for key in ['my_config_file']:
#         os.environ[key] = environ.get(key, '')
#     from server import app as _application

#     return _application(environ, start_response)
