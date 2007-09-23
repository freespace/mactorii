#!/usr/bin/env python
# encoding: utf-8
"""
pyx.pyx

Created by Shu Ning Bian on 2007-09-23.
Copyright (c) 2007 . All rights reserved.
"""

import sys
import os
def pix_sum(x,y):
	"""Returns a tuple which is the sum of the tuples given"""
	return ((x[0])+y[0], x[1]+y[1], x[2]+y[2])

def pix_diff(x,y):
	"""Returns a tuple which is the difference of the tuples given"""
	return ((x[0])-y[0], x[1]-y[1], x[2]-y[2])
	
def pyx_transform_array(input):
	"""Performs wavelet transform on the input, destorys input"""
	length = len(input)
	output = [0]*length

	if length%2:
		length=length-1

	while(True):
		length=length/2
		for i from 0 <= i < length:
			s = pix_sum(input[i*2], input[i*2+1])
			d = pix_diff(input[i*2], input[i*2+1])
			output[i] = s
			output[length+i] = d
			
		if length == 1:
			return output
		else:
			input = output
	raise Exception

def main():
	pass


if __name__ == '__main__':
	main()

