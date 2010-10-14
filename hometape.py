#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main file of hometape

import config, tapetv,tools
from downloader import Downloader
import wx
import os, sys

class HometapeFrame(wx.Frame):
	def __init__(self):
		# Load our configuration
		self.config = config.read_conf()
		
		self.lastdir = os.getcwd()
		self.dldr_instances = []
		self.results = []
		
		# Force User to input a valid config
		if not ( self.config['temp_dir'] and self.config['rtmpdump_path'] and self.config['ffmpeg_path'] ):
			conf_dlg = config.ConfDlg(self.config)
			if conf_dlg.ShowModal() == wx.ID_OK:
				self.config = conf_dlg.getconf()
				conf_dlg.Destroy()
			else:
				conf_dlg.Destroy()
				fuckedup_dlg = wx.MessageDialog(None, 'hometape can not work without a valid configuration.', 'Exiting', wx.OK | wx.ICON_ERROR)
				fuckedup_dlg.ShowModal()
				fuckedup_dlg.Destroy()
				sys.exit()
		
		# All the GUI stuff
		wx.Frame.__init__(self, None, title="hometape",size=(300,500))
		
		menubar = wx.MenuBar()
		
		m_file = wx.Menu()
		m_quit = wx.MenuItem(m_file, wx.ID_EXIT, "&Exit")
		m_file.AppendItem(m_quit)
		
		m_edit = wx.Menu()
		m_preferences = wx.MenuItem(m_edit, wx.ID_PREFERENCES, "&Preferences")
		m_edit.AppendItem(m_preferences)
		
		m_help = wx.Menu()
		m_info = wx.MenuItem(m_help, wx.ID_ABOUT, "&About")
		m_help.AppendItem(m_info)
		
		menubar.Append(m_file, "&File")
		menubar.Append(m_edit, "&Edit")
		menubar.Append(m_help, "&Help")
		
		self.SetMenuBar(menubar)
		
		self.mainpanel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		vbox.Add((-1,2))
		
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		
		grid = wx.FlexGridSizer(2,2,5,5)
		search_label = wx.StaticText(self.mainpanel, label="Search:")
		self.search_box = wx.TextCtrl(self.mainpanel, style=wx.TE_PROCESS_ENTER)
		search_by_label = wx.StaticText(self.mainpanel, label="Search by:")
		search_by_choices = [
			"Artist + Title",
			"Artist",
			"Artist (exactly)",
			"Title",
			"Title (exact)"
		]
		self.search_by_cb = wx.Choice(self.mainpanel, choices=search_by_choices)
		grid.AddMany([
			(search_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.search_box, 1, wx.EXPAND),
			(search_by_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.search_by_cb, 1, wx.EXPAND)
		])
		grid.AddGrowableCol(1, 1)
		hbox1.Add(grid, 1, wx.EXPAND, 0)
		
		search_btn = wx.Button(self.mainpanel, id=wx.ID_FIND)
		hbox1.Add(search_btn, 0, wx.EXPAND | wx.LEFT, 5)
		
		vbox.Add(hbox1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 2)
		
		hline = wx.StaticLine(self.mainpanel, style=wx.LI_HORIZONTAL)
		vbox.Add(hline, 0, wx.ALL | wx.EXPAND, 5)
		
		results_cap = wx.StaticText(self.mainpanel, label="Search results:")
		vbox.Add(results_cap, 0, wx.ALL | wx.EXPAND, 2)
		
		self.result_list = wx.ListBox(self.mainpanel, style=wx.LB_SINGLE)
		self.result_list.SetMinSize((200,200))
		vbox.Add(self.result_list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 2)
		
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.dl_flv = wx.Button(self.mainpanel, label="Download FLV Video")
		self.dl_mp3 = wx.Button(self.mainpanel, label="Download MP3 Audio")
		self.dl_flv.Disable()
		self.dl_mp3.Disable()
		hbox2.Add(self.dl_flv, 1, wx.RIGHT | wx.EXPAND, 5)
		hbox2.Add(self.dl_mp3, 1, wx.EXPAND, 0)
		vbox.Add(hbox2, 0, wx.EXPAND | wx.ALL, 2)
		
		vbox.Fit(self)
		
		self.mainpanel.SetSizer(vbox)
		self.SetMinSize(self.GetSize())
		
		try:
			self.SetSize(self.config['last_size'])
		except KeyError:
			pass
		
		self.SetIcon(wx.Icon(os.path.join(tools.progdir(), "wm_icon.png"), wx.BITMAP_TYPE_PNG))
		
		# Events
		self.Bind(wx.EVT_MENU, self.on_info, id=m_info.GetId())
		self.Bind(wx.EVT_MENU, self.on_prefs, id=m_preferences.GetId())
		self.Bind(wx.EVT_MENU, self.on_close, id=m_quit.GetId())
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.Bind(wx.EVT_BUTTON, self.on_search, id=search_btn.GetId())
		self.Bind(wx.EVT_TEXT_ENTER, self.on_search, id=self.search_box.GetId())
		self.Bind(wx.EVT_LISTBOX, self.on_select, id=self.result_list.GetId())
		self.Bind(wx.EVT_BUTTON, self.on_dl_flv, id=self.dl_flv.GetId())
		self.Bind(wx.EVT_BUTTON, self.on_dl_mp3, id=self.dl_mp3.GetId())
	
	def on_close(self, event):
		for dldr in self.dldr_instances:
			try:
				dldr.Close()
			except:
				continue
		self.config['last_size'] = self.GetSize()
		config.save_conf(self.config)
		self.Show(False)
		self.Destroy()
	
	def on_search(self, event):
		# Has the input got enough chars?
		if len(self.search_box.GetValue()) >= 2:
			# Querying tape.tv
			wx.BeginBusyCursor()
			self.results = tapetv.search(self.search_box.GetValue(), self.search_by_cb.GetCurrentSelection())
			result_formatted = ["%s - %s" % (r['artist'],r['title']) for r in self.results]
			self.result_list.Set(result_formatted)
			wx.EndBusyCursor()
	
	def on_select(self, event):
		selections = self.result_list.GetSelections()
		if len(selections) == 0:
			self.dl_flv.Disable()
			self.dl_mp3.Disable()
		else:
			self.dl_flv.Enable()
			self.dl_mp3.Enable()
	
	def on_dl_flv(self, event):
		self.dl_something(False)
	
	def on_dl_mp3(self, event):
		self.dl_something(True)
	
	def dl_something(self, convert):
		index, = self.result_list.GetSelections()
		wc = "Flash Videos (*.flv)|*.flv" if not convert else "MP3 Audio (*.mp3)|*.mp3"
		suggested_filename = '%s - %s.%s' % (self.results[index]['artist'], self.results[index]['title'], 'mp3' if convert else 'flv')
		save_dlg = wx.FileDialog(self, defaultDir=self.lastdir, defaultFile=suggested_filename, wildcard=wc, style=wx.SAVE | wx.OVERWRITE_PROMPT)
		savehere = ''
		if save_dlg.ShowModal() == wx.ID_OK:
			savehere = save_dlg.GetPath()
		save_dlg.Destroy()
		if savehere:
			self.lastdir = os.path.dirname(savehere)
			self.dldr_instances.append(Downloader(self.results[index]['id'], savehere, self.config, convert))
	
	def on_info(self, event):
		description = "hometape is a tool for downloading music\nvideos from tape.tv."
		licence = "hometape is licensed under the MIT license for free software." + """
Copyright (c) 2010 Kevin Chabowski

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHE-
THER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE"""
		info = wx.AboutDialogInfo()
		info.SetIcon(wx.Icon(os.path.join(tools.progdir(), "hometape_slogan.png"), wx.BITMAP_TYPE_PNG))
		info.SetName('hometape')
		info.SetVersion('0.2')
		info.SetDescription(description)
		info.SetCopyright('(C) 2010 Kevin Chabowski')
		info.SetLicence(licence)
		info.AddDeveloper('Kevin Chabowski')
		
		wx.AboutBox(info)
	
	def on_prefs(self, event):
		conf_dlg = config.ConfDlg(self.config)
		if conf_dlg.ShowModal() == wx.ID_OK:
			self.config = conf_dlg.getconf()
			conf_dlg.Destroy()
		else:
			conf_dlg.Destroy()
			self.Show(False)
			fuckedup_dlg = wx.MessageDialog(None, 'hometape can not work without a valid configuration.', 'Exiting', wx.OK | wx.ICON_ERROR)
			fuckedup_dlg.ShowModal()
			fuckedup_dlg.Destroy()
			self.Destroy()


if __name__ == '__main__':
	app = wx.App()
	ht_frame = HometapeFrame()
	ht_frame.Show()
	app.MainLoop()
