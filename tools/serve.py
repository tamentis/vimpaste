#!/usr/bin/env python

"""
Debugging WSGI server.
"""

from wsgiref.simple_server import make_server
from vimpaste import app

httpd = make_server('localhost', 9000, app)
print("Serving vimpaste for debug on http://localhost:9000/.")
httpd.serve_forever()
