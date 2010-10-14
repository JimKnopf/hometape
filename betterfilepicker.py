#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, os

class BetterFilePicker(wx.Panel):
	def __init__(self, parent, id=-1, pickdir=False, path=''):
		"""NOT a full replacement for FilePickerCtrl!"""
		wx.Panel.__init__(self, parent, id)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		self.__path = path
		self.pickdir = pickdir
		
		self.textbox = wx.TextCtrl(self, value=path)
		mw,mh = self.textbox.GetMinSize()
		self.textbox.SetMinSize((200,mh))
		self.dlg_opener = wx.Button(self, label="...")
		
		hbox.Add(self.textbox, 1, wx.EXPAND, 0)
		hbox.Add(self.dlg_opener, 0, wx.LEFT | wx.EXPAND, 5)
		
		self.SetSizer(hbox)
		
		self.Bind(wx.EVT_BUTTON, self.__on_dlg_opener, id=self.dlg_opener.GetId())
		self.Bind(wx.EVT_TEXT, self.__on_textbox, id=self.textbox.GetId())
	
	def __is_valid_path(self, path):
		if os.path.exists(path):
			if self.pickdir:
				return os.path.isdir(path)
			else:
				return os.path.isfile(path)
	
	def __on_textbox(self, event):
		newpath = self.textbox.GetValue()
		self.__path = newpath
		self.send_event()
	
	def __on_dlg_opener(self, event):
		# Prepare dialog
		if self.pickdir:
			dialog = wx.DirDialog(self, defaultPath=self.__path, style=wx.DD_DIR_MUST_EXIST)
		else:
			dialog = wx.FileDialog(self, defaultDir=os.path.dirname(self.__path), defaultFile=self.__path, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if dialog.ShowModal() == wx.ID_OK:
			newpath = dialog.GetPath()
			if self.__is_valid_path(newpath):
				self.__path = newpath
				self.textbox.SetValue(newpath)
				self.send_event()
		dialog.Destroy()
	
	def send_event(self):
		event = wx.CommandEvent(wx.wxEVT_COMMAND_FILEPICKER_CHANGED, self.GetId()) # Misusing the button event
		event.SetEventObject(self)
		self.GetEventHandler().ProcessEvent(event)
	
	def GetPath(self):
		return self.__path
	
	def SetPath(self, path):
		self.__path = path
		self.textbox.SetValue()
