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

#import pyx

def open(path):
	"""opens a file as a WaveletImage"""
	return WaveletImage(path)
	
class WaveletImage(object):
	"""A lazy wavelet transform class"""
	def __init__(self, path):
		super(WaveletImage, self).__init__()
		
		"""
		Load the image from given path, using PIL, converts it into YIQ colour space
		"""
		rgb2yiq = (
			 0.299,	 0.587,	 0.114,	0,
			 0.595716,	-0.274453,	-0.321263,	0,
			 0.211456,	-0.522591,	 0.311135, 	0
			)
			
		rgb2yuv = (
			 0.299,	 0.587,	 0.114,	 0,
			-0.14713,	 -0.28886,	 0.436,	 0,
			 0.615,	-0.51498,	-0.10001,	 0,
			)
			
		im = Image.open(path)
		self.size = im.size
		im.thumbnail(config.img_size,Image.ANTIALIAS)
		im = im.convert("RGB")
		
		self.data = im.convert("RGB", rgb2yiq).getdata()
		#self.data = im.convert("RGB", rgb2yuv).getdata()
		self.im = im
		self.wavelets = None
		self.sig = None
	
	def cleanup(self):
		"""
		Frees wavelets data and reverts image to rgb. This method should only be called
		*after* calling .signature() at least once
		"""
		self.wavelets = None
		self.data = None
		
	def pix_sum(self, x,y):
		"""Returns a tuple which is the sum of the tuples given"""
		return (x[0]+y[0], x[1]+y[1], x[2]+y[2])
	
	def pix_diff(self, x,y):
		"""Returns a tuple which is the difference of the tuples given"""
		return (x[0]-y[0], x[1]-y[1], x[2]-y[2])
	
	def signature(self):
		"""Returns a signature tuple based on the input which is expected to be the
		wavelet transform of an image
		"""
		
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

			if length > config.taps:
				lower = tmp[config.taps/2]
				upper = tmp[length-config.taps/2]
			else:
				lower = tmp[length/4]
				upper = tmp[length-length/4]

			# keep up to config.taps number of significant values, storing only their 
			# position and sign
			for i in xrange(length):
				if i <1:
					continue
					
				val = input[i][band]
				if val > upper or val < lower:
					if len(sig[band]) <= config.taps:
						# clamp it to either 1 or -1 or 0
						if val > 0:
							val = 1
						elif val < 0:
							val = -1
							
						sig[band].append((i,val))
					else:
						# if more than the require number of signatures has been
						# gathered for this band, break out
						break

		return set(sig[0]), set(sig[1]), set(sig[2])
			
	def signature2(self):
		"""Returns a signature tuple based on the input which is expected to be the
		wavelet transform of an image
		"""		
		if not self.wavelets:
			self.transform()
			
		input = self.wavelets	
		length=len(input)/8
	
		sig=[[], [], []]
		tmp=[0]*length
	
		for band in xrange(3):
			# copy the values in the current band into a tmp buffer
			for i in xrange(length):
				tmp[i] = (input[i][band], i)
			
			# sorting by x[0]^2 because we want both negative and positive significant
			# coefficients
			tmp.sort(key = lambda x: x[0]*x[0])
			
			# take config.taps number of significan coefficients if we have enough
			if length > config.taps:
				sig[band] = tmp[-config.taps:]
			else:
				# otherwise take the entire tmp
				sig[band] = tmp[:]
		
			# normalise the signatures, research shows this is better
			tmpsig = []*len(sig[band])
			for s in sig[band]:
				v = s[0]
				l = s[1]
				if v > 0:
					v = 1
				elif v < 0:
					v = -1
				s = (l,v)
				tmpsig.append(s)
			sig[band]=tmpsig[:]
			# print sig[band]
			
		return set(sig[0]), set(sig[1]), set(sig[2])
	
	def transform_array(self, input):
		"""Performs wavelet transform on the input, destorys input"""
		length = len(input)
		output = [0]*length
		
		while(True):
			length/=2
			
			for i in xrange(length):
				# s = self.pix_sum(input[i*2], input[i*2+1])
				# d = self.pix_diff(input[i*2], input[i*2+1])
				# output[i] = s
				# output[length+i] = d
				
				x = input[i*2]
				y = input[i*2+1]
				output[i] = (x[0]+y[0], x[1]+y[1], x[2]+y[2])
				output[length+i] = (x[0]-y[0], x[1]-y[1], x[2]-y[2])

			if length == 1:
				return output
			else:
				input = output[:length*2]

		raise Exception
		
	def transform(self):
		"""
		Performs a wavelet transform on the given image
		"""
		assert self.data != None, "Did you call .cleanup() before .signature()?"
		input = list(self.data)
		
		self.wavelets = self.transform_array(input)
		#self.wavelets = pyx.pyx_transform_array(input)
		return
		
		# rows, cols = self.im.size
		# 
		# # perform a transform on each row
		# for row in xrange(rows):
		# 	input[row*cols:(row+1)*cols] = self.transform_array(input[row*cols:(row+1)*cols])
		# 	
		# transposed=[]
		# # now transpose the flatten array
		# for col in xrange(cols):
		# 	for row in xrange(rows):
		# 			transposed.append(input[row*cols+col])
		# 			
		# input = transposed;
		# cols, rows = self.im.size
		# 
		# # perform another transform on each row
		# # perform a transform on each row
		# for row in xrange(rows):
		# 	input[row*cols:(row+1)*cols] = self.transform_array(input[row*cols:(row+1)*cols])
		# 
		# transposed=[]
		# # now transpose the flatten array
		# for col in xrange(cols):
		# 	for row in xrange(rows):
		# 			transposed.append(input[row*cols+col])
		# 			
		# self.wavelets = transposed
				
	def compare(self, other):
		"""Compars this wavelet transform to another, returning a tuple of similarness"""
		sig = other.signature()
		
		score = []
		for b in xrange(3):
			score.append(config.weights[b]*len(self.sig[b].intersection(sig[b])))
		
		return tuple(score)
			
def main():
	pass


if __name__ == '__main__':
	main()

