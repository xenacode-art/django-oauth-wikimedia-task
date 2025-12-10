#!/usr/bin/env python3
import os
import sys

# Add the src directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Use PyMySQL as a drop-in replacement for mysqlclient
import pymysql
pymysql.install_as_MySQLdb()
# Patch version to satisfy Django's version check
pymysql.version_info = (2, 2, 7, "final", 0)
pymysql.__version__ = "2.2.7"

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oauth_app.settings')

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Alias for uwsgi compatibility
app = application
