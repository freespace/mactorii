"""
This is a setup.py script generated by py2applet

Usage:
    python2.5 setup.py py2app

Copyright 2007 Shu Ning Bian freespace@gmail.com
Licensed for distribution under the GPL version 2, check COPYING for details
"""

from setuptools import setup,find_packages
import sys


import config

APP = ['mactorii.py']
OPTIONS = {'argv_emulation': True, 'iconfile': 'mactorii.icns'}

if sys.platform == "darwin":
	SETUP_REQUIRES=['py2app']
else:
	SETUP_REQUIRES=[]

setup(
   version=mactorii.version,
   description='Image browser with sort, cluster ability based on wavelet transforms',
   author='Shu Ning Bian',
   author_email='freespace@gmail.com',
   url='http://trac.pictorii.com/mactorii/',
    
    app=APP,
	name="mactorii",
    options={'py2app': OPTIONS},
    py_modules = ['mactorii', 'config','wavelet'],# 'Imaging', 'pyglet'],
	setup_requires = SETUP_REQUIRES,
	license = "Creative Commons Attribution-Noncommercial-Share Alike 2.5 Australia License",
    keywords = "image, browser, wavelet, sort",
)
