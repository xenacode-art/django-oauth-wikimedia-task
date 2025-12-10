#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Use PyMySQL as a drop-in replacement for mysqlclient
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        # Patch version to satisfy Django's version check
        pymysql.version_info = (2, 2, 7, "final", 0)
        pymysql.__version__ = "2.2.7"
    except ImportError:
        pass  # PyMySQL not installed, probably running locally with SQLite

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oauth_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
