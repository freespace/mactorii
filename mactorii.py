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
import shutil
import Tkinter
import tkFileDialog

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
images = dict()
baselines = []

renderables = None

yoffset = 0
xoffset = 0
xmotion = 0

rows = 1
cols = 1
	
clickx = 0
clicky = 0

hoverx = 0
hovery = 0

selected = None
hovering_over = None

last_deleted = []

fps_display = None

display_picture = None

def on_mouse_motion(x,y,dx,dy):
	global hoverx
	global hovery
	
	hoverx = x
	hovery = y
	
def on_mouse_press(x, y, button, modifiers):
	global images
	global selected
	global xoffset
	
	if hovering_over != None:
		print "%s selected"%(hovering_over)
		selected = images[hovering_over]
		update_renderables()
		xoffset = 0
		
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
	global images
	global renderables
	global hovering_over
	global last_deleted
	global fps_display
	global display_picture
	global win
	
	if symbol == key.LEFT:
		xmotion = 10
		if modifier == key.MOD_SHIFT:
			xmotion*=2
				
	if symbol == key.RIGHT:
		xmotion -= 10
		if modifier == key.MOD_SHIFT:
			xmotion*=2	

	if hovering_over != None:
		if symbol == key.D:
			assert images.has_key(hovering_over)
			del images[hovering_over]
			update_renderables()
			shutil.move(hovering_over, "%s/%s"%(config.trash_dir, os.path.basename(hovering_over)))
			last_deleted.append(hovering_over)
			
			display_picture = None
		
	if symbol == key.U and len(last_deleted) > 0:
		last = last_deleted.pop()
		shutil.move("%s/%s"%(config.trash_dir, os.path.basename(last)), last)
		load_file(last)
		update_renderables()
		
	if symbol == key.F:
		if fps_display:
			fps_display = None
		else:
			fps_display = clock.ClockDisplay()		
			
	if symbol == key.C:
		cluster_renderables()
		
	if symbol == key.W and modifier == key.MOD_CTRL:
		sys.exit(0)
		
	if symbol == key.Q and modifier == key.MOD_COMMAND:
		sys.exit(0)
		
	if symbol == key.Q:
		sys.exit(0)
	
	if symbol == key.V:
		if display_picture != None:
			display_picture = None
		elif hovering_over != None:
			im = Image.open(hovering_over)
			im.thumbnail((win.width, win.height),Image.ANTIALIAS)
			im = im.convert("RGB")
			im = im.transpose(Image.FLIP_TOP_BOTTOM)
			
			display_picture = pyglet_image.ImageData(im.size[0],im.size[1],"RGB",im.tostring())
			
def strip_width():
	"""returns the width of the strip in pixels"""
	global rows
	return math.ceil(1.0 * len(files)/rows) * config.crop_size
	
def on_resize(width, height):
	"""Recomputes yoffset and row"""
	global yoffset
	global xoffset
	global rows
	global cols 

	p = xoffset/strip_width()
	
	rows = int(height/config.crop_size) 
	cols = math.floor(len(files)/rows)+1
	
	yoffset = (height - rows * config.crop_size)/2
	yoffset = height-yoffset-config.crop_size
	
	# compute the new xoffset
	xoffset = p * strip_width()

def signature_compare(sig1, sig2):
	score=[]
	for b in xrange(3):
		score.append(config.weights[b]*len(sig1[b].intersection(sig2[b])))
		
	return sum(score)
	
def cluster_func(item):
	global cols
	global rows
	
	item_sig = item[1][2]
	
	mul = 113
	score = 0
	for sig in baselines:
		score += signature_compare(sig, item_sig)
		score*=mul
		
	return score
	
def cluster_renderables():
	"""cluster renderables by their score against the 2 base lines"""
	global images
	global renderables
	
	renderables = images.items()
	
	# sort the renderables
	renderables.sort(key=cluster_func)
	
	#for i, r in enumerate(renderables):
		
	
def update_renderables():
	global images
	global renderables
	global selected
	
	renderables = images.items()
	
	if selected != None:
		renderables.sort(key=sort_func)

def sort_func(item):
	assert selected != None
	
	selected_sig = selected[2]
	item_sig = item[1][2]
	
	return -signature_compare(selected_sig, item_sig)

def load_baseline(file):
	"""loads baseline pictures"""
	global baselines
	
	print "processing baseline: %s"%(file)
	wi = wavelet.open(file)
	sig = wi.signature()
	baselines.append(sig)
	
def load_file(file):
	"""loads the files given in the command line"""
	
	global images
	
	print "processing file: %s"%(file)
	try:
		wi = wavelet.open(file)
	except:
		print "can't load file: %s"%(file)
		return
		
	sig = wi.signature()
	
	# resize the image so the smallest dimension is config.crop_size
	im = wi.im
	w,h = im.size
	s=0
	if w > h:
		s = 1.0*config.crop_size/h
	else:
		s = 1.0*config.crop_size/w
	
	w = int(w*s*1.2)
	h = int(h*s*1.2)
	
	im.thumbnail((w, h), Image.ANTIALIAS)
	
	# crop out the centre crop_size square to use a thumbnail
	midx = w/2
	midy = h/2
	box = (midx-config.crop_size/2, midy-config.crop_size/2, midx+config.crop_size/2, midy+config.crop_size/2)
	im=im.crop(box)
	
	# make a pyglet image out of it
	im = im.transpose(Image.FLIP_TOP_BOTTOM)
	psurf=pyglet_image.ImageData(im.size[0],im.size[1],"RGB",im.tostring())
	
	# add to our dictionary
	images[ unicode(file,'utf-8').encode('ascii', 'ignore') ] = (psurf, None, sig, wi.size)
	
def window_setup():
	"""sets up our window"""
	win = window.Window(resizable=True, visible=False)
	
	win.push_handlers(on_resize)
	win.push_handlers(on_key_press)
	win.push_handlers(on_key_release)
	win.push_handlers(on_mouse_press)
	win.push_handlers(on_mouse_release)
	win.push_handlers(on_mouse_motion)
	
	return win
	
def font_setup():
	"""sets up fonts"""
	return font.load(config.font_name, config.font_size, bold=True)

def is_over_image(x, y, mousex, mousey):
	if mousex < 0 or mousey < 0:
		return False
		
	if mousex < x or mousex > x + config.crop_size:
		return False
		
	if mousey < y or mousey > y + config.crop_size:
			return False
				
	return True
	
def trash_setup():
	try:
		os.mkdir(config.trash_dir)
	except:
		return
	
def main():
	global xoffset
	global xmotion
	global yoffset
	global rows
	global cols
	global files
	global win
	global clickx
	global clicky
	global hoverx
	global hovery
	global selected
	global hovering_over
	global images
	global renderables
	global fps_display
	global display_picture
		
	# order is important here. window_setup must be setup first! Likewise with font
	win = window_setup()
	ft = font_setup()
	
	root = Tkinter.Tk()
	root.withdraw()
	if (sys.platform != "win32") and hasattr(sys, 'frozen'):
		root.tk.call('console', 'hide')
				
	if len(sys.argv) < 2:
		dirname = tkFileDialog.askdirectory(parent=root,initialdir="~",title='Please select a directory')
		
			
		if len(dirname ) > 0:
			import dircache
			ls = dircache.listdir(dirname)
			ls = list(ls)
			dircache.annotate(dirname, ls)
			
			files = ["%s%s%s"%(dirname,os.path.sep,e) for e in ls if not e.endswith('/')]
		else:
			sys.exit(1)
	else:		
		files = sys.argv[1:]
			
	win.set_visible()
	trash_setup()	
	
	assert win != None
	assert ft != None
	
	image_pattern = pyglet_image.SolidColorImagePattern((0,0,0,1))
	
	clock.set_fps_limit(30)
	
	win.set_visible()
	unloaded = list(files)
	unloaded_baselines = list(config.baselines)
	
	while not win.has_exit:
		clock.tick()
		win.dispatch_events()
		glClear(GL_COLOR_BUFFER_BIT)
		
		if len(unloaded_baselines) > 0:
			f = unloaded_baselines.pop()
			str = "|||||"*len(unloaded_baselines)
			t = font.Text(ft, str, 0, config.text_yoffset)
			t.draw()
			win.flip()
			
			load_baseline(f)
			continue
			
		if len(unloaded) > 0:
			f = unloaded.pop()
			t = font.Text(ft, f, 0, config.text_yoffset)
			t.draw()			
			#win.flip()
			
			load_file(f)
			
			#if len(unloaded) == 0:
			update_renderables()
			#continue
			
		if display_picture != None:
			w = display_picture.width
			h = display_picture.height
			display_picture.blit((win.width-w)/2,(win.height-h)/2)
			win.flip()
			continue
			
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
		hovering_over = None
		blit_position = ()
		for filename, image in renderables:
			img = image[0]
			img.blit(x,y)
							
			if is_over_image(x,y,hoverx, hovery):
				# draw some information
				pix_size = font.Text(ft,"%dx%d"%(image[3][0], image[3][1]), x, y+config.text_yoffset)
				pix_name = font.Text(ft, os.path.basename(filename), x, y+config.text_yoffset+int(pix_size.height))						

				w = pix_size.width
				if pix_name.width > pix_size.width:
					w = pix_name.width
					
				if w < config.crop_size:
					w = config.crop_size
				else:
					w = math.ceil(w/config.crop_size)*config.crop_size
						
				w = int(w)
				h = int(pix_name.height+pix_size.height+config.text_yoffset)
				text_bg = image_pattern.create_image(w,h)
				blit_position=(x, y)
				
				hovering_over = filename

			drawn+=1
			y-=config.crop_size
			
			if drawn % rows == 0:
				x+=config.crop_size
				y = yoffset

		if fps_display:
			fps_display.draw()
		if hovering_over:
			text_bg.blit(blit_position[0], blit_position[1])
			pix_name.draw()
			pix_size.draw()
			
		win.flip()
	
if __name__ == '__main__':
	main()

