#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import os, sys
import tools
from betterfilepicker import BetterFilePicker

try:
	import cPickle as pickle
except:
	import pickle

def read_conf():
	try:
		return pickle.load(open(tools.homefile('.hometape.pickle'), 'rb'))
	except:
		return make_default()

def make_default():
	config = {}
	if os.name == 'nt':
		for appname in ['rtmpdump','ffmpeg']:
			try:
				config[appname+'_path'] =  tools.findapp(appname+'.exe', [tools.progdir()+'\\tooldir\\%s\\bin'%appname])
			except tools.NotFoundError:
				config[appname+'_path'] = ''
		config['temp_dir'] = os.environ['TEMP']
	else: # posix
		for appname in ['rtmpdump','ffmpeg']:
			try:
				config[appname+'_path'] = tools.findapp(appname)
			except tools.NotFoundError:
				config[appname+'_path'] = ''
		config['temp_dir'] = '/tmp'
	return config

def save_conf(conf):
	pickle.dump(conf, open(tools.homefile('.hometape.pickle'), 'wb'))

# This Config dialog is buggy, so we do not use it now. Only default configuration...
class ConfDlg(wx.Dialog):
	def __init__(self, config):
		# Read out config file
		self.config = config
		
		# GUI stuff
		wx.Dialog.__init__(self, None, title=_("Preferences"))
		
		self.mainpanel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		header_font = wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, weight=wx.FONTWEIGHT_BOLD, style=wx.FONTSTYLE_NORMAL, underline=False)
		header = wx.StaticText(self.mainpanel, label=_("Preferences"))
		header.SetFont(header_font)
		vbox.Add(header, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		
		vbox.Add(wx.StaticLine(self.mainpanel, style=wx.LI_HORIZONTAL),1 ,wx.ALL | wx.EXPAND, 5)
		
		conftable = wx.FlexGridSizer(3, 2, 5, 5)
		
		conflabels = [ wx.StaticText(self.mainpanel, label=x) for x in [_('Temporary Directory:'), _('RTMPDump executable:'), _('FFMpeg executable:')]]
		self.tempdir_ctrl = BetterFilePicker(self.mainpanel, path=self.config['temp_dir'], pickdir=True)
		self.rtmpdump_ctrl  = BetterFilePicker(self.mainpanel, path=self.config['rtmpdump_path'])
		self.ffmpeg_ctrl  = BetterFilePicker(self.mainpanel, path=self.config['ffmpeg_path'])
		
		conftable.AddMany([
			(conflabels[0],0,wx.ALIGN_CENTER_VERTICAL), (self.tempdir_ctrl,  1, wx.EXPAND | wx.ALIGN_RIGHT),
			(conflabels[1],0,wx.ALIGN_CENTER_VERTICAL), (self.rtmpdump_ctrl, 1, wx.EXPAND | wx.ALIGN_RIGHT),
			(conflabels[2],0,wx.ALIGN_CENTER_VERTICAL), (self.ffmpeg_ctrl,   1, wx.EXPAND | wx.ALIGN_RIGHT)
		])
		conftable.AddGrowableCol(1, 1)
		
		vbox.Add(conftable,0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		
		vbox.Add(wx.StaticLine(self.mainpanel, style=wx.LI_HORIZONTAL),1 ,wx.ALL | wx.EXPAND, 5)
		
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.alert = wx.StaticText(self.mainpanel, label=_("Some path is wrong!"))
		self.alert.SetForegroundColour(wx.Colour(255,0,0))
		hbox.Add(self.alert, 1, wx.EXPAND, 0)
		resetbutton = wx.Button(self.mainpanel, label=_("Reset"))
		hbox.Add(resetbutton, 0, wx.LEFT, 5)
		self.closebutton = wx.Button(self.mainpanel, id=wx.ID_CLOSE, label=_("Close"))
		hbox.Add(self.closebutton, 0, wx.LEFT, 5)
		vbox.Add(hbox, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 2)
		
		self.mainpanel.SetSizer(vbox)
		vbox.Fit(self)
		
		self.SetMinSize(self.GetSize())
		
		# Bind stuff
		
		self.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_tempdir, id=self.tempdir_ctrl.GetId())
		self.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_rtmpdump, id=self.rtmpdump_ctrl.GetId())
		self.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_ffmpeg, id=self.ffmpeg_ctrl.GetId())
		self.Bind(wx.EVT_BUTTON, self.on_reset, id=resetbutton.GetId())
		self.Bind(wx.EVT_BUTTON, self.on_close, id=self.closebutton.GetId())
		self.Bind(wx.EVT_CLOSE, self.on_close)
		
		self.isokay()
	
	def getconf(self):
		return self.config
	
	def isokay(self):
		if self.config['temp_dir'] and self.config['rtmpdump_path'] and self.config['ffmpeg_path']:
			self.alert.SetLabel('')
			return True
		else:
			self.alert.SetLabel(_('Some path is wrong!'))
			return False
	
	def on_tempdir(self,event):
		if os.path.isdir(self.tempdir_ctrl.GetPath()):
			self.config['temp_dir'] = self.tempdir_ctrl.GetPath()
		else:
			self.config['temp_dir'] = ''
		self.isokay()
	
	def on_rtmpdump(self, event):
		if os.path.isfile(self.rtmpdump_ctrl.GetPath()):
			self.config['rtmpdump_path'] = self.rtmpdump_ctrl.GetPath()
		else:
			self.config['rtmpdump_path'] = ''
		self.isokay()
	
	def on_ffmpeg(self, event):
		if os.path.isfile(self.ffmpeg_ctrl.GetPath()):
			self.config['ffmpeg_path'] = self.ffmpeg_ctrl.GetPath()
		else:
			self.config['ffmpeg_path'] = ''
		self.isokay()
	
	def on_reset(self, event):
		self.config = make_default()
		self.tempdir_ctrl.SetPath(self.config['temp_dir'])
		self.rtmpdump_ctrl.SetPath(self.config['rtmpdump_path'])
		self.ffmpeg_ctrl.SetPath(self.config['ffmpeg_path'])
		self.isokay()
	
	def on_close(self, event):
		self.Show(False)
		self.EndModal(wx.ID_OK if self.isokay() else wx.ID_CANCEL)

