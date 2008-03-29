#!/usr/bin/env python
# encoding: utf-8
"""
wavelet.py

Created by Shu Ning Bian on 2007-09-22.
Copyright (c) 2007 . All rights reserved.
Licensed for distribution under the GPL version 2, check COPYING for details.

Signature returned by this class is a dictionary with key of (band, location) value of
either 1 or -1. Location is z = y*columns + x.
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
		self.signature = None
	
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
	
	def get_signature(self):
		"""Returns a signature tuple based on the input which is expected to be the
		wavelet transform of an image
		"""		
		if not self.wavelets:
			self.transform()
		if self.signature:
			return self.signature

		self.signature = {}
		input = self.wavelets	
		length=len(input)/8
	
		tmp=[0]*length
		for band in xrange(3):
			# copy the values in the current band into a tmp buffer
			for i in xrange(length):
				tmp[i] = (input[i][band], i)
			
			sig = []
			
			# sorting by x[0]^2 because we want both negative and positive significant
			# coefficients
			tmp.sort(key = lambda x: x[0]*x[0])
			
			# take config.taps number of significan coefficients if we have enough
			if length > config.taps:
				sig = tmp[:config.taps]
			else:
				# otherwise take the entire tmp
				sig = tmp[:]
			
			# normalise the signatures, research shows this is better	
			for s in sig:
				v = s[0]
				l = s[1]
				
				# clamp to [-1,1]
				v = max(-1, min(1, v))
				k = (band, l)
				self.signature[k] = v

		return self.signature
	
	def transform_array(self, input):
		"""
		Performs wavelet transform on the input, destorys input, 
		see http://en.wikipedia.org/wiki/Discrete_wavelet_transform
		"""
		length = len(input)
		output = [0]*length
		
		while(True):
			length/=2
			
			for i in xrange(length):
				x = input[i*2]
				y = input[i*2+1]
				output[i] = (x[0]+y[0], x[1]+y[1], x[2]+y[2])
				output[length+i] = (x[0]-y[0], x[1]-y[1], x[2]-y[2])

			if length <= 1:
				return output
			
			input = output[:length*2]

		raise Exception
		
	def transform(self):
		"""
		Performs a wavelet transform on the given image
		"""
		assert self.data != None, "Did you call .cleanup() before .signature()?"
		input = list(self.data)
		
		self.wavelets = self.transform_array(input)
		return
		
	def compare(self, other):
		"""Compars this wavelet transform to another, returning a tuple of similarness"""
		sig1 = other.get_signature()
		sig2 = self.get_signature()

		return signature_compare(sig1, sig2)

			
def	signature_compare(sig1, sig2):
	score = 0
	for key,value in sig1.items():
		if sig2.has_key(key):
			if sig2[key] == value:
				score += config.weights[key[0]]
			else:
				score += config.weights[key[0]] * 0.5

		
	return score

def main():
	pass


if __name__ == '__main__':
	main()

