#!/usr/bin/env python

from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

setup(
    name = 'bottle-sqlalchemy',
    version = '0.2',
    description = 'SQLAlchemy integration for Bottle.',
    author = 'Iuri de Silvio',
    author_email = 'iurisilvio@gmail.com',
    url = 'http://www.github.com/iurisilvio/bottle-sqlalchemy',
    license = 'MIT',
    platforms = 'any',
    py_modules = [
        'bottle_sqlalchemy'
    ],
    requires = [
        'bottle (>=0.9)',
        'sqlalchemy'
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass = {'build_py': build_py}
)
