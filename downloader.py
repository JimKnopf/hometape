#!/usr/bin/env python

import wx
import tapetv, tools
import os
import urllib2
from uuid import uuid4
from subproc_thread import SubprocThread

class Downloader(wx.Frame):
	"""wxPython frame/window, which displays the download process"""
	def __init__(self, tapetv_id, saveto, config, convert=True):
		"""Initializes the Downloader frame
		
		convert -- If True, video will be converted to mp3
		tapetv_id -- ID of the stream
		saveto -- The path where the output should be saved to
		config -- A configuration dictionary, at least this entry:
		          'temp_dir', 'rtmpdump_path', 'ffmpeg_path'"""
		
		# Before doing anything, we will get the stream informations
		self.streaminfo = tapetv.streaminfo(tapetv_id)
		if self.streaminfo is None:
			raise ValueError('tapetv_id is an invalid ID')
		
		# save other important parameters
		self.temp_dir = config['temp_dir']
		self.rtmpdump_path = config['rtmpdump_path']
		self.ffmpeg_path = config['ffmpeg_path']
		self.convert = convert
		self.saveto = saveto
		
		if os.path.exists(saveto):
			try:
				os.remove(saveto)
			except:
				pass
		
		self.tmpfile = ''
		if convert:
			if not self.ffmpeg_path:
				raise tools.NotFoundError(_('ffmpeg was not found. You need it to convert to mp3.'))
			self.tmpfile = os.path.join(self.temp_dir, 'hometape_'+str(uuid4()))
		
		self.step = 'juststarted'
		
		# placeholders
		self.SPT_rtmpdump = None
		self.SPT_ffmpeg   = None
		
		# GUI stuff
		wx.Frame.__init__(self, None, title=_("Downloading \"%s\"") % self.streaminfo['title'], size=(300, 180), style= wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
		
		self.mainpanel = wx.Panel(self, -1)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		img_panel = wx.Panel(self.mainpanel, -1)
		hbox.Add(img_panel, 0, wx.ALL | wx.EXPAND, 2)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		self.status = wx.StaticText(self.mainpanel, label=_("Downloading"))
		vbox.Add(self.status, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND | wx.ALIGN_TOP, 2)
		
		vbox.Add((-1,8))
		
		self.gauge = wx.Gauge(self.mainpanel, style=wx.GA_HORIZONTAL)
		self.gauge.SetRange(1000)
		vbox.Add(self.gauge, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 2)
		
		vbox.Add((-1,8))
		
		self.quit_btn = wx.Button(self.mainpanel, pos=(2, 90), size=(296, 28), id=wx.ID_CANCEL)
		vbox.Add(self.quit_btn, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 2)
		
		hbox.Add(vbox, 1, wx.EXPAND, 0)
		
		hbox.Fit(self)
		
		# Download and resize video image
		tmpfile = os.path.join(config['temp_dir'], 'hometape_'+str(uuid4()))
		try:
			url = urllib2.urlopen(self.streaminfo['image'])
			fh = open(tmpfile, 'wb')
			fh.write(url.read())
			fh.close()
			url.close()
			imh = wx.Image(tmpfile, wx.BITMAP_TYPE_PNG if self.streaminfo['image'].split('.')[-1] == 'png' else wx.BITMAP_TYPE_JPEG)
			os.remove(tmpfile)
			w = imh.GetWidth()
			h = imh.GetHeight()
			ww,wh = self.GetSize()
			w /= h/wh
			imh.Rescale(w,wh)
			video_bitmap = wx.StaticBitmap(img_panel)
			video_bitmap.SetBitmap(wx.BitmapFromImage(imh))
			img_panel.SetMinSize((w,wh))
			hbox.Fit(self)
		except:
			pass
		
		self.mainpanel.SetSizer(hbox)
		
		# Timer
		self.maintimer = wx.Timer(self)
		
		# Binding events
		self.Bind(wx.EVT_CLOSE, self.on_cancel)
		wx.EVT_TIMER(self, self.maintimer.GetId(), self.on_maintimer)
		self.quit_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
		
		# Fire up Timer
		self.maintimer.Start(100, False)
		
		# Show yourself
		self.Show()
		
	def on_cancel(self, event):
		try:
			self.SPT_rtmpdump.terminate()
		except:
			pass
		try:
			self.SPT_ffmpeg.terminate()
		except:
			pass
		try:
			self.maintimer.Stop()
		except:
			pass
		try:
			os.remove(self.tmpfile)
		except:
			pass
		self.Show(False)
		self.Destroy()
	
	def on_maintimer(self, event):
		if self.step == 'juststarted':
			self.SPT_rtmpdump = SubprocThread([
				self.rtmpdump_path,
				'-r',
				'rtmpe://cp68509.edgefcs.net/ondemand?auth=%s&aifp=v001&ovpfv=1.1' % self.streaminfo['token'],
				'-y', self.streaminfo['url'],
				'-o', (self.tmpfile if self.convert else self.saveto)], os.name=='nt')
			self.step = 'dumping_rtmp';
		elif self.step == 'dumping_rtmp':
			if self.SPT_rtmpdump.running:
				new_percent = -1
				for logentry in self.SPT_rtmpdump.stdout_log:
					pr_start = logentry.find('(')
					if pr_start == -1:
						continue
					pr_end = logentry.find('%)')
					if pr_end == -1:
						continue
					try:
						new_percent = int(float(logentry[pr_start+1:pr_end])*10)
					except:
						continue
				if new_percent != -1:
					if self.convert:
						new_percent /= 2
					self.gauge.SetValue(new_percent)
			else:
				if self.convert:
					self.SPT_ffmpeg = SubprocThread([
						self.ffmpeg_path,
						'-i', self.tmpfile,
						'-f', 'mp3',
						'-acodec', 'libmp3lame',
						'-ab', '192000',
						self.saveto
					], os.name=='nt')
					self.step = 'converting'
				else:
					self.step = 'done'
		elif self.step == 'converting':
			self.status.SetLabel(_('Converting'))
			if not self.SPT_ffmpeg.running:
				try:
					os.remove(self.tmpfile)
				except:
					pass
				self.step = 'done'
		else: # done
			self.status.SetLabel(_('Done'))
			self.gauge.SetValue(1000)
			self.maintimer.Stop()

