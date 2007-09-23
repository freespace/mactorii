#!/usr/bin/env python
# encoding: utf-8
"""
mactorii.py

Created by Shu Ning Bian on 2007-09-23.
Copyright (c) 2007 . All rights reserved.
"""

import sys
import os

import wavelet
import config

from pyglet.gl import *
from pyglet import window
from pyglet import image as pyglet_image
from pyglet import clock 

yoffset = 0
xoffset = 0
rows = 0
	
def on_resize(width, height):
	"""Recomputes yoffset and row"""
	global yoffset
	global xoffset
	global rows
	
	rows = int(height/config.crop_size)	
	
	yoffset = (height - rows * config.crop_size)/2
	yoffset = height-yoffset-config.crop_size
	
def main():
	global xoffset
	global yoffset
	global rows
	
	files = sys.argv[1:]
	images = dict()
	for file in files:
		print "processing file: %s"%(file)
		wi = wavelet.open(file)
		sig = wi.signature()
		wi.cleanup()
		img = pyglet_image.load(file)
		region = img.get_region(x=img.width/2-config.crop_size/2, \
								y=img.height/2-config.crop_size/2, \
								width=config.crop_size, height=config.crop_size)
		images[file] = (region, img, 0)
		
		
	win = window.Window(resizable=True, visible=False)
	win.push_handlers(on_resize)
	
	clock.set_fps_limit(30)
	win.set_visible()
	while not win.has_exit:
		clock.tick()
		win.dispatch_events()
		glClear(GL_COLOR_BUFFER_BIT)
		
		x = xoffset
		y = yoffset
		drawn = 0
		for image in images.values():
			img = image[0]
			img.blit(x,y)
			
			drawn+=1
			y-=config.crop_size
			
			if drawn % rows == 0:
				x+=config.crop_size
				y = yoffset
				
		win.flip()
	
if __name__ == '__main__':
	main()

