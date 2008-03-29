#!/usr/bin/env python
# encoding: utf-8
# Copyright 2007 Shu Ning Bian freespace@gmail.com
# Licensed for distribution under the GPL version 2, check COPYING for details
# Mactorii is intended as a image organiser/viewer in the spirit of qiv
from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext
setup(
	name = "pyx",
	ext_modules=[
		Extension("pyx", ["pyx.pyx"], libraries = [])
		],
	cmdclass = {'build_ext': build_ext}
)

def main():
	pass


if __name__ == '__main__':
	main()

