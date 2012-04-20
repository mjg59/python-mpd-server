#!/usr/bin/env python

from distutils.core import setup

setup(name='python-mpd-server',
      version='1.0',
      description='Create Mpd Server in Python',
      author='kedals',
      author_email='kedals0@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      py_modules=["mpdserver","command_base","command_skel"],
     )
