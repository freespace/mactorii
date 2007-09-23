#!/usr/bin/env python
# encoding: utf-8
"""
mactorii.py

Created by Shu Ning Bian on 2007-09-23.
Copyright (c) 2007 . All rights reserved.
"""

import sys
import os
import math
import Image

import wavelet
import config

from pyglet.gl import *
from pyglet import window
from pyglet import image as pyglet_image
from pyglet import clock 
from pyglet.window import key
from pyglet.window import mouse
from pyglet import font

files = None
win = None

yoffset = 0
xoffset = 0
rows = 1
xmotion = 0
	
clickx = 0
clicky = 0

hoverx = 0
hovery = 0

selected = None

def on_mouse_motion(x,y,dx,dy):
	global hoverx
	global hovery
	
	hoverx = x
	hovery = y
	
def on_mouse_press(x, y, button, modifiers):
	global clickx
	global clicky
	
	if button == mouse.LEFT:
		clickx = x
		clicky = y
		
def on_mouse_release(x,y,button, modifiers):
	global clickx
	global clicky
	
	return
	if button == mouse.LEFT:
		clickx = -1
		clicky = -1
			
def on_key_release(symbol, modifier):
	global xoffset
	global xmotion

	if symbol == key.LEFT:
		xmotion = 0
	
	if symbol == key.RIGHT:
		xmotion = 0
		
def on_key_press(symbol, modifier):
	global xoffset
	global xmotion

	if symbol == key.LEFT:
			xmotion = 10
	
	if symbol == key.RIGHT:
			xmotion -= 10

def strip_width():
	"""returns the width of the strip in pixels"""
	global rows
	return math.ceil(1.0 * len(files)/rows) * config.crop_size
	
def on_resize(width, height):
	"""Recomputes yoffset and row"""
	global yoffset
	global xoffset
	global rows
	
	p = xoffset/strip_width()
	
	rows = int(height/config.crop_size) 
	
	yoffset = (height - rows * config.crop_size)/2
	yoffset = height-yoffset-config.crop_size
	
	# compute the new xoffset
	xoffset = p * strip_width()
	
def sort_func(item):
	assert selected != None
	
	selected_sig = selected[2]
	item_sig = item[1][2]
	
	score = []
	for b in xrange(3):
		score.append(config.weights[b]*len(selected_sig[b].intersection(item_sig[b])))
	return -sum(score)

def load_files(files):
	"""loads the files given in the command line"""
	images = dict()
	
	for file in files:
		print "processing file: %s"%(file)
		wi = wavelet.open(file)
		sig = wi.signature()
		wi.im.thumbnail((config.crop_size, config.crop_size), Image.ANTIALIAS)
		wi.im = wi.im.transpose(Image.FLIP_TOP_BOTTOM)
		psurf=pyglet_image.ImageData(wi.im.size[0],wi.im.size[1],"RGB",wi.im.tostring())

		images[	unicode(file,'utf-8').encode('ascii', 'ignore')	] = (psurf, None, sig, wi.size)
		
	return images
	
def window_setup():
	"""sets up our window"""
	win = window.Window(resizable=True, visible=False)
	
	win.push_handlers(on_resize)
	win.push_handlers(on_key_press)
	win.push_handlers(on_key_release)
	win.push_handlers(on_mouse_press)
	win.push_handlers(on_mouse_release)
	win.push_handlers(on_mouse_motion)
	
	win.set_visible()
	
	return win
	
def font_setup():
	"""sets up fonts"""
	return font.load(config.font_name, config.font_size)

def is_over_image(x, y, mousex, mousey):
	if mousex < 0 or mousey < 0:
		return False
		
	if mousex < x or mousex > x + config.crop_size:
		return False
		
	if mousey < y or mousey > y + config.crop_size:
			return False
				
	return True
	
def main():
	global xoffset
	global xmotion
	global yoffset
	global rows
	global files
	global win
	global clickx
	global clicky
	global hoverx
	global hovery
	global selected
	
	files = sys.argv[1:]
	images = load_files(files)

	win = window_setup()
	ft = font_setup()
	
	assert win != None
	assert ft != None
	
	clock.set_fps_limit(30)
	
	renderables = images.items()
	
	while not win.has_exit:
		clock.tick()
		win.dispatch_events()
		glClear(GL_COLOR_BUFFER_BIT)
		
		if xmotion < 0:
			if strip_width() + xoffset > win.width:
				xoffset+=xmotion
				
		if xmotion > 0:
			if xoffset < 0:
				xoffset+=xmotion
				
		x = xoffset 
		y = yoffset
		pix_name = None
		pix_size = None
		
		drawn = 0
		for filename, image in renderables:
			img = image[0]
			img.blit(x,y)
			
			if is_over_image(x,y,clickx, clicky):
				print "%s selected"%(filename)
				selected = image
				renderables.sort(key=sort_func)
				
				clickx = -1
				clicky = -1
				
				xoffset = 0
				break
				
			if is_over_image(x,y,hoverx, hovery):
				pix_name = 	font.Text(ft, filename, hoverx, hovery+config.font_size+5)
				pix_size = font.Text(ft, "%dx%d"%(image[3][0], image[3][0]), hoverx, hovery+5)
			drawn+=1
			y-=config.crop_size
			
			if drawn % rows == 0:
				x+=config.crop_size
				y = yoffset
		if pix_name:
			pix_name.draw()		
		if pix_size:
			pix_size.draw()
				
		win.flip()
	
if __name__ == '__main__':
	main()

