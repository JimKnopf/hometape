#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess, os, time
from threading import Thread

if os.name == 'nt':
	import win32process

class SubprocThread(Thread):
	"""Thread which runs and supervises a subprocess"""
	
	def __init__(self, proc_params, mswin_nowin=False):
		Thread.__init__(self)
		self.stdout_log = []
		self.running = False
		self.returned = 0
		if mswin_nowin:
			self.proc = subprocess.Popen(
				proc_params,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				creationflags = win32process.CREATE_NO_WINDOW
			)
		else:
			self.proc = subprocess.Popen(
				proc_params,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT
			)
		self.start()
	
	def terminate(self):
		if self.running:
			self.proc.terminate()
			while self.running:
				time.sleep(0.1)
	
	def run(self):
		self.running = True
		while True:
			data = self.proc.stdout.read(100)
			if data == '': # EOF reached -> Process stopped
				break
			
			self.stdout_log.append(data)
			if len(self.stdout_log) > 10:
				del self.stdout_log[0]
		self.returned = self.proc.wait()
		self.running = False

