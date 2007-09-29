#!/usr/bin/env python
# encoding: utf-8
"""
waveletUnitTest.py

Created by Shu Ning Bian on 2007-09-23.
Copyright (c) 2007 . All rights reserved.
"""

import unittest
import wavelet

class waveletUnitTest(unittest.TestCase):
	def setUp(self):
		"""
		steve@solaris:~/code/mactorii$ md5sum blueships.jpg 
		9c5e36768e6dad37b17244eb54ca9b9d  blueships.jpg
		steve@solaris:~/code/mactorii$ md5sum hiero.jpg 
		1aa200df65ff0d99ffc2b9543963bed4  hiero.jpg
		"""
		self.wi=[]
		self.wi.append(wavelet.open("bluexmas2k2.jpg"))
		self.wi.append(wavelet.open("hiero.jpg"))
		
	def testSignature(self):
		return
		"""Checking signatures are still correct"""
		hashes = [
			[891130499,380051862,687850410],
			[-2134815841,-775538075,-627883134]
			]
		for i in xrange(len(self.wi)):
			sig = self.wi[i].signature()
			for j in xrange(3):
				s = sig[j]
				h = hash(tuple(s))
				assert  h == hashes[i][j], "bad hash. expected %d got %d"%(hashes[i][j], h)
	
	def testCleanup(self):
		return
		"""Make sure the cleanup function is still working"""
		for i in xrange(len(self.wi)):
			self.wi[i].signature()
			self.wi[i].cleanup()
		
		self.testSignature()
					
if __name__ == '__main__':
	unittest.main()