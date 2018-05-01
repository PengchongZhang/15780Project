#!/usr/bin/env python
class Task:
	index = 0
	estVal = 0
	need_save = True
	
	def __init__(self, index, estVal):
		self.index = index
		self.estVal = estVal