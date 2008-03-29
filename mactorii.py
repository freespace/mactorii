#!/usr/bin/env python
# encoding: utf-8
"""
mactorii.py

Created by Shu Ning Bian on 2007-09-23.
Copyright (c) 2007 . All rights reserved.
Licensed for distribution under the GPL version 2, check COPYING for details.
"""

import sys
import os
import Image
import math
import shutil
import Tkinter
import tkFileDialog
import time

import wavelet
import config

from pyglet.gl import *
from pyglet import window
from pyglet import image as pyglet_image
from pyglet import clock 
from pyglet.window import key
from pyglet.window import mouse
from pyglet import font

version=0.78

class MactoriiApplication:
	renderables_key_func = lambda x : 0

	files = None
	win = None
	# key is the filename, value is another dictionary, with keys
	# surface, signature, size, cluster key
	images = dict()
	unloaded = None
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

	root = None
	
	def on_mouse_motion(self,x,y,dx,dy):
		self.hoverx = x
		self.hovery = y
		
	def toggle_full_view(self):
		"""enters into full view if possible"""
		
		if self.hovering_over != None:
			if self.display_picture != None:
				self.display_picture = None
			elif self.hovering_over != None:
				im = Image.open(self.hovering_over)
				im.thumbnail((self.win.width, self.win.height),Image.ANTIALIAS)
				im = im.convert("RGB")
				im = im.transpose(Image.FLIP_TOP_BOTTOM)
			
				self.display_picture = pyglet_image.ImageData(im.size[0],im.size[1],"RGB",im.tostring())
			
	def on_mouse_press(self,x, y, button, modifiers):
		self.toggle_full_view()
			
	def on_mouse_release(self,x,y,button, modifiers):
		
		return
		if button == mouse.LEFT:
			self.clickx = -1
			self.clicky = -1
				
	def on_key_release(self,symbol, modifier):
		if symbol == key.LEFT:
			self.xmotion = 0
		
		if symbol == key.RIGHT:
			self.xmotion = 0
			
	def on_key_press(self,symbol, modifier):
		if symbol == key.LEFT:
			self.xmotion = 10
					
		if symbol == key.RIGHT:
			self.xmotion -= 10

		if modifier == key.MOD_SHIFT:
			self.xmotion*=4

		if self.hovering_over != None:
			if symbol == key.D:
				assert self.images.has_key(self.hovering_over)
				del self.images[self.hovering_over]
				self.update_renderables()
				shutil.move(self.hovering_over, "%s/%s"%(os.path.basename(self.hovering_over),config.trash_dir))
				self.last_deleted.append(self.hovering_over)
				
				self.display_picture = None
			
		if symbol == key.U and len(self.last_deleted) > 0:
			self.last = self.last_deleted.pop()
			shutil.move("%s/%s"%(config.trash_dir, os.path.basename(last)), self.last)
			self.load_file(last)
			self.update_renderables()
			
		if symbol == key.F:
			if self.fps_display:
				self.fps_display = None
			else:
				self.fps_display = clock.ClockDisplay()		
				
		if symbol == key.C:
			self.cluster_renderables()
			
		if symbol == key.W and modifier == key.MOD_CTRL:
			sys.exit(0)
			
		if symbol == key.Q and modifier == key.MOD_COMMAND:
			sys.exit(0)
			
		if symbol == key.Q:
			sys.exit(0)
		
		if symbol == key.V:
			self.toggle_full_view()
			
		if symbol == key.S:
			if self.hovering_over != None:
				print "sorting by %s"%(self.hovering_over)
				self.selected = self.images[self.hovering_over]
				self.renderables_key_func = self.sort_func
				self.update_renderables()
				self.xoffset = 0
		
		if symbol == key.O:
			dirname = tkFileDialog.askdirectory(parent=self.root,initialdir="~",title='Please select a directory')

			if len(dirname ) > 0:
				import dircache
				ls = dircache.listdir(dirname)
				ls = list(ls)
				dircache.annotate(dirname, ls)

				files = ["%s%s%s"%(dirname,os.path.sep,e) for e in ls if not e.endswith('/')]
				self.unloaded = list(files)
				
				self.images = dict()
					
		if symbol == key.R:
			self.unloaded = list(files)
			self.images = dict()
			
	def strip_width(self):
		"""returns the width of the strip in pixels"""
		return math.ceil(1.0 * len(self.files)/self.rows) * config.crop_size
		
	def on_resize(self,width, height):
		"""Recomputes yoffset and row"""
		p = self.xoffset/self.strip_width()
		
		self.rows = int(height/config.crop_size) 
		self.cols = math.floor(len(self.files)/self.rows)+1
		
		self.yoffset = (height - self.rows * config.crop_size)/2
		self.yoffset = height-self.yoffset-config.crop_size
		
		# compute the new xoffset
		self.xoffset = p * self.strip_width()
		
		self.toggle_full_view()
		self.toggle_full_view()

	def cluster_func(self,item):
		return self.images[item[0]]['cluster key']

	def images_to_renderables(self,images):
		"""returns images.items() as a set of (filename, python surface, image size)"""
		return [(filename, (data['surface'], data['size'])) for filename, data in images.items()]

	def cluster_renderables(self):
		"""cluster renderables by their score against the 2 base lines"""
		self.renderables_key_func = self.cluster_func
		key = 0
		filename_sigs = [(filename, data['signature']) for filename, data in self.images.items()]
		seed = filename_sigs[0][0]
		del filename_sigs[0]

		done = False
		while len(filename_sigs):
			key+=1
			sig = self.images[seed]['signature']
			filename_sigs.sort(key = lambda x: -wavelet.signature_compare(sig, x[1]))
			f = filename_sigs[0][0]
			self.images[f]['cluster key']=key
			del filename_sigs[0]
			seed = f
		self.update_renderables()
		
	def update_renderables(self,sort=True):
		if self.renderables:
			n = self.images_to_renderables(self.images)
			if len(n) != len(self.renderables):
				# images were added, so just re-assign renderables
				self.renderables = n
			elif len(n) < len(self.renderables):
				# images were removed, we need to remove them from renderables too
				self.renderables = n
				
		else:
			self.renderables = self.images_to_renderables(self.images)
			
		if sort:
			self.renderables.sort(key=self.renderables_key_func)

	def sort_func(self,item):
		assert self.selected != None
		
		selected_sig = self.selected['signature']
		item_sig = self.images[item[0]]['signature']
		
		return -wavelet.signature_compare(selected_sig, item_sig)

		
	def load_file(self,file):
		"""loads the files given in the command line"""
		
		#print "processing file: %s"%(file)
		
		try:
			wi = wavelet.open(file)
		except:
			print "can't load file: %s"%(file)
			return
			
		sig = wi.get_signature()
		
		# get the pre-loaded image from wavelet
		im = wi.im
		w,h = im.size

		# resize the image so the smallest dimension is config.crop_size	
		s=0
		if w > h:
			s = 1.0*config.crop_size/h
		else:
			s = 1.0*config.crop_size/w
		
		w = int(w*s*1.3)
		h = int(h*s*1.3)

		im=im.resize((w, h), Image.ANTIALIAS)
		
		# crop out the centre crop_size square to use a thumbnail
		midx = w/2
		midy = h/2
		box = (midx-config.crop_size/2, midy-config.crop_size/2, midx+config.crop_size/2, midy+config.crop_size/2)
		im=im.crop(box)
		
		# make a pyglet image out of it
		psurf = image_to_psurf(im)
		
		# add to our dictionary
		self.images[ file ] = {'surface':psurf, 'signature':sig, 'size':wi.size, 'cluster key':0}
	def to_unicode(self,s):
		return unicode(s, 'utf-8', 'ignore')
		
	def setup_window(self):
		"""sets up our window"""
		win = window.Window(resizable=True, visible=False, caption='mactorii v0.%s'%(version))
		
		win.push_handlers(self.on_resize)
		win.push_handlers(self.on_key_press)
		win.push_handlers(self.on_key_release)
		win.push_handlers(self.on_mouse_press)
		win.push_handlers(self.on_mouse_release)
		win.push_handlers(self.on_mouse_motion)
		
		glEnable(GL_BLEND) 
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
		
		return win
		
	def setup_font(self):
		"""sets up fonts"""
		return font.load(config.font_name, config.font_size, bold=True)

	def is_over_image(self,x, y, mousex, mousey):
		if mousex < 0 or mousey < 0:
			return False
			
		if mousex < x or mousex > x + config.crop_size:
			return False
			
		if mousey < y or mousey > y + config.crop_size:
				return False
					
		return True
		
	def setup_trash(self):
		try:
			os.mkdir(config.trash_dir)
		except:
			return
		
	def find_common_signature(self,signatures):
		common_sig = [set()]*config.bands
		
		for i in xrange(len(signatures)):
			for b in xrange(config.bands):
				if i == 0:
					common_sig[b] = signatures[i][b]
				else:
					common_sig[b] = common_sig[b].intersection(signatures[i-1][b])
								
		return common_sig
		
	def main(self):
		# order is important here. setup_window must be setup first! Likewise with font
		self.win = self.setup_window()
		ft = self.setup_font()
		
		self.root = Tkinter.Tk()
		self.root.withdraw()
		
		if (sys.platform != "win32") and hasattr(sys, 'frozen'):
			self.root.tk.call('console', 'hide')
					
		if len(sys.argv) < 2:
			dirname = tkFileDialog.askdirectory(parent=self.root,initialdir="~",title='Please select a directory')
						
			if len(dirname ) > 0:
				import dircache
				ls = dircache.listdir(dirname)
				ls = list(ls)
				dircache.annotate(dirname, ls)
				
				self.files = ["%s%s%s"%(dirname,os.path.sep,e) for e in ls if not e.endswith('/')]
			else:
				sys.exit(1)
		else:		
			self.files = sys.argv[1:]
				
		self.win.set_visible()
		self.setup_trash()	
		
		assert self.win != None
		assert ft != None
		
		# generate our oft used black background
		image_pattern = pyglet_image.SolidColorImagePattern((0,0,0,1))
	

		# limit fps to reduce cpu usage
		clock.set_fps_limit(config.fps)
	
		# start loading files
		self.win.set_visible()
		self.unloaded = list(self.files)
		self.update_renderables()
		print "loading %d files"%(len(self.unloaded))
		start_time = time.time()
		while not self.win.has_exit:
			time_passed = clock.tick()
			
			self.win.dispatch_events()
			glClear(GL_COLOR_BUFFER_BIT)
			
			if len(self.unloaded) > 0:
				f = self.unloaded.pop()
				t = font.Text(ft, self.to_unicode(f), config.text_yoffset, config.text_yoffset)
				t.draw()			
				#win.flip()
				
				self.load_file(f)
				
				if len(self.unloaded) %3 == 0:
					self.update_renderables(sort=False)

				if len(self.unloaded) == 0:
					print "loading took %f seconds"%(time.time()-start_time)
					
			else:
				# raise Exception
				pass
			
			# if we need to display a full image, do so
			if self.display_picture != None:
				w = self.display_picture.width
				h = self.display_picture.height
				self.display_picture.blit((self.win.width-w)/2,(self.win.height-h)/2)
				self.win.flip()
				continue
			
			# adjust the xoffset if required 		
			if self.xmotion < 0:
				if self.strip_width() + self.xoffset > self.win.width:
					self.xoffset+=self.xmotion * time_passed / config.xmotion_time 
					
			if self.xmotion > 0:
				if self.xoffset < 0:
					self.xoffset+=self.xmotion * time_passed / config.xmotion_time 

			# clamp xoffset to 0 if xoffset is > 0
			self.xoffset = min(self.xoffset, 0)
			
			# render the tiles
			x = self.xoffset 
			y = self.yoffset
			pix_name = None
			pix_size = None
			drawn = 0
			self.hovering_over = None
			blit_position = ()
			for filename, image in self.renderables:
				img = image[0]
				
				if ( x >= -config.crop_size and x < self.win.width):
					img.blit(x,y)				
					
					# if the cursor is over this tile, render some information
					if self.is_over_image(x,y,self.hoverx, self.hovery) and (not pix_name or filename != pix_name.text):
						# draw some information
						pix_size = font.Text(ft,"%dx%d"%(image[1][0], image[1][1]), x, y+config.text_yoffset)
						pix_name = font.Text(ft, self.to_unicode(os.path.basename(filename)), x, y+config.text_yoffset+int(pix_size.height))						
						
						# calculate the black background required to make text show up
						# width needs to be in integer multiples of tile size
						w = max(pix_size.width, pix_name.width)
						w = max(config.crop_size, (w/config.crop_size+1)*config.crop_size)
							
						w = int(w)
						h = int(pix_name.height+pix_size.height+config.text_yoffset)
						text_bg = image_pattern.create_image(w,h)
						blit_position=(x, y)
					
						# remember which image we are hovering over so when a click is seen
						# we know which image to display 
						self.hovering_over = filename

				drawn+=1
				y-=config.crop_size
				
				if drawn % self.rows == 0:
					x+=config.crop_size
					y = self.yoffset

			# everything drawn here is drawn over everything else
			if self.fps_display:
				self.fps_display.draw()
			
			if self.hovering_over:
				text_bg.blit(blit_position[0], blit_position[1])
				pix_name.draw()
				pix_size.draw()
		
			self.win.flip()
	
def	image_to_psurf(im):
	im = im.transpose(Image.FLIP_TOP_BOTTOM)
	return pyglet_image.ImageData(im.size[0],im.size[1],"RGB",im.tostring())

if __name__ == '__main__':
	app = MactoriiApplication()
	app.main()
