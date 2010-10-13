#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import os, sys
import tools

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
				config[appname+'_path'] =  tools.findapp(appname+'.exe', [tools.progdir()+'\\tools\\%s\\bin'%appname])
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
"""class ConfDlg(wx.Frame):
	def __init__(self):
		# Read out config file
		self.config = read_conf()
		print self.config
		
		# GUI stuff
		wx.Frame.__init__(self, None, title="Configuration")
		
		self.mainpanel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		header_font = wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, weight=wx.FONTWEIGHT_BOLD, style=wx.FONTSTYLE_NORMAL, underline=False)
		header = wx.StaticText(self.mainpanel, label="Configuration")
		header.SetFont(header_font)
		vbox.Add(header, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		
		vbox.Add((-1,5),1,wx.EXPAND, 0)
		
		conftable = wx.FlexGridSizer(3, 2, 5, 5)
		
		conflabels = [ wx.StaticText(self.mainpanel, label=x) for x in ['Temporary Directory:', 'RTMPDump executable:', 'FFMpeg executable:']]
		self.tempdir_ctrl = wx.DirPickerCtrl(self.mainpanel, path='/home', style=wx.DIRP_USE_TEXTCTRL)
		self.rtmpdump_ctrl  = wx.FilePickerCtrl(self.mainpanel, path=self.config['rtmpdump_path'], style=wx.FLP_USE_TEXTCTRL)
		self.ffmpeg_ctrl  = wx.FilePickerCtrl(self.mainpanel, path=self.config['ffmpeg_path'], style=wx.FLP_USE_TEXTCTRL)
		
		conftable.AddMany([
			(conflabels[0],0,wx.ALIGN_CENTER_VERTICAL), (self.tempdir_ctrl,  1, wx.EXPAND | wx.ALIGN_RIGHT),
			(conflabels[1],0,wx.ALIGN_CENTER_VERTICAL), (self.rtmpdump_ctrl, 1, wx.EXPAND | wx.ALIGN_RIGHT),
			(conflabels[2],0,wx.ALIGN_CENTER_VERTICAL), (self.ffmpeg_ctrl,   1, wx.EXPAND | wx.ALIGN_RIGHT)
		])
		conftable.AddGrowableCol(1, 1)
		
		vbox.Add(conftable,0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		
		vbox.Add((-1,5),1,wx.EXPAND, 0)
		
		self.closebutton = wx.Button(self.mainpanel, label="Close")
		vbox.Add(self.closebutton, 0, wx.RIGHT | wx.ALIGN_RIGHT, 2)
		
		vbox.Fit(self)
		self.mainpanel.SetSizer(vbox)
		
		self.SetMinSize(self.GetEffectiveMinSize())
		
		self.Show()
	
	def update_config(self, event):
		pass
	
	def get_config(self):
		return self.config"""
		

if __name__ == '__main__':
	app = wx.App()
	mf = ConfDlg()
	app.MainLoop()
