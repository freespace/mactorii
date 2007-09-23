#!/usr/bin/env python
# encoding: utf-8
"""
wavelet.py

Created by Shu Ning Bian on 2007-09-22.
Copyright (c) 2007 . All rights reserved.
"""

import sys
import os
import Image
import config

class WaveletTransform(object):
	"""A lazy wavelet transform class"""
	def __init__(self, path):
		super(WaveletTransform, self).__init__()
		
		"""
		load the image from given path, using PIL, converts it into YIQ colour space
		"""
		rgb2yiq = (
			0.299,	 0.587,	 0.114,	0,
			0.596,	-0.275,	-0.321,	0,
			0.212,	-0.523,	 0.311, 0
			)
		im = Image.open(path)
		im = im.resize(config.img_size)
		im = im.convert("RGB")
		self.im=im.convert("RGB", rgb2yiq)
		self.wavelets = None
		self.sig = None
		
	def pix_sum(self, x,y):
		"""returns a tuple which is the sum of the tuples given"""
		return ((x[0])+y[0], x[1]+y[1], x[2]+y[2])
	
	def pix_diff(self, x,y):
		"""returns a tuple which is the difference of the tuples given"""
		return ((x[0])-y[0], x[1]-y[1], x[2]-y[2])
	
	def signature(self):
		"""returns a signature tuple based on the input which is expected to be the
		wavelet transform of an image
		"""
		
		if self.sig:
			return self.sig
			
		if not self.wavelets:
			self.transform()
		input = self.wavelets	
		length=len(input)/8
	
		sig=[[], [], []]
		tmp=[0]*length
	
		for band in xrange(3):
			# copy the values in the current band into a tmp buffer
			for i in xrange(length):
				tmp[i] = input[i][band]
			
			# sort the values to determine upper and lower cut offs for significance
			tmp.sort()
			lower = tmp[config.taps/2]
			upper = tmp[length-config.taps/2]
		
			# keep up to config.taps number of significant values, storing only their 
			# position and sign
			for i in xrange(length):
				val = input[i][band]
				if val > upper or val < lower:
					if len(sig[band]) <= config.taps:
						# clamp it to either 1 or -1 or 0
						if val > 0:
							val = 1
						else:
							val = -1
						sig[band].append((i,val))
					else:
						# if more than the require number of signatures has been
						# gathered for this band, break out
						break
			sig[band].sort()
		
		self.sig = (set(sig[0]), set(sig[1]), set(sig[2]))
		return self.sig
	
	def transform_array(self, input):
		"""docstring for transform a single array"""
		length = len(input)
		output = [0]*length
	
		if length%2:
			length-=1
	
		while(True):
			length/=2
			for i in xrange(length):
				s = self.pix_sum(input[i*2], input[i*2+1])
				d = self.pix_diff(input[i*2], input[i*2+1])
				output[i] = s
				output[length+i] = d
				
			if length == 1:
				return output
			else:
				input = output
		raise Exception
		
	def transform(self):
		"""
		performs a wavelet transform on the given image
		"""
		input = list(self.im.getdata())
		
		self.wavelets = self.transform_array(input)
		return
		
		rows, cols = self.im.size
		
		# perform a transform on each row
		for row in xrange(rows):
			input[row*cols:(row+1)*cols] = self.transform_array(input[row*cols:(row+1)*cols])
			
		transposed=[]
		# now transpose the flatten array
		for col in xrange(cols):
			for row in xrange(rows):
					transposed.append(input[row*cols+col])
					
		input = transposed;
		cols, rows = self.im.size
		
		# perform another transform on each row
		# perform a transform on each row
		for row in xrange(rows):
			input[row*cols:(row+1)*cols] = self.transform_array(input[row*cols:(row+1)*cols])
		
		transposed=[]
		# now transpose the flatten array
		for col in xrange(cols):
			for row in xrange(rows):
					transposed.append(input[row*cols+col])
					
		self.wavelets = transposed
				
	def compare(self, other):
		"""compars this wavelet transform to another, returning a tuple of similarness"""
		sig = other.signature()
		
		score = []
		for b in xrange(3):
			score.append(config.weights[b]*len(self.sig[b].intersection(sig[b])))
		
		return tuple(score)
			
def main():
	pass


if __name__ == '__main__':
	main()

