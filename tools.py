#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

class NotFoundError(Exception):
	def __init__(self, msg=''):
		self.msg = msg
	
	def __str__(self):
		return self.msg

def homefile(fn):
	return os.path.join(os.path.expanduser('~'), fn)

def progdir():
	return os.path.abspath(os.path.dirname(sys.argv[0]))

def findapp(appname, additional_paths=[]):
	"""Find an application
	
	This will search 'appname' in the global searchpath and in our own directory.
	
	Returns the absolute path to the application.
	Raises tools.NotFoundError if the application was not found.
	"""
	# building our search list
	searchlist = os.environ['PATH'].split(';' if os.name == 'nt' else':')
	searchlist.append(progdir())
	searchlist += additional_paths
	
	for path in searchlist:
		try:
			for fn in os.listdir(path):
				if fn == appname:
					return os.path.join(path,fn)
		except:
			continue
	raise NotFoundError('\'%s\' was not found.')
