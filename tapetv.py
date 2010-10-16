#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib, urllib2
import xml.etree.ElementTree as etree

def _download_and_parse_xml(url, params, fix_raw_data=None):
	"""This function will download and parse an XML document.
	
	url -- The URL which should be downloaded
	params -- Parameters for the URL (list of 2-element-tuples)
	
	returns an ElementTree node or None, if somethingwent wrong
	"""
	
	# Prepare URL...
	if len(params) > 0:
		url += '?' + urllib.urlencode(params)
	
	# ...Download...
	try:
		urlhandle = urllib2.urlopen(url)
		rawxml = urlhandle.read()
		urlhandle.close()
		
		if fix_raw_data is not None:
			rawxml = fix_raw_data(rawxml)
	
		# ...and parse!
		return etree.fromstring(rawxml)
	except:
		return None

def search(query, filterby):
	"""Searching music videos in the tape.tv database.
	
	query -- Search for this
	filterby -- One of these:
	            0 - Artist + Title
	            1 - Title
	            2 - Title (exact)
	            3 - Title
	            4 - Title (exact)
	
	Returns a list of dictionaries which have these following keys:
	'id', 'artist', 'title'"""
	
	# Get XML tree
	results = _download_and_parse_xml(
		'http://www.tape.tv/tapeMVC/tape/search/search',
		[
			('telly', 'tapetv'),
			('source', 'search'),
			('artistOrTitle', query)
		])
	
	if results == None:
		return []
	
	# Get informations
	videos = []
	for vid in results:
		try:
			videos.append({
				'id':     vid.get('id'),
				'artist': vid.find('artist').text,
				'title':  vid.find('title').text
			})
		except:
			continue
	
	filters = [
		lambda x: True,
		lambda x: x['artist'].lower().find(query.lower()) != -1,
		lambda x: x['artist'].lower() == query.lower(),
		lambda x: x['title'].lower().find(query.lower()) != -1,
		lambda x: x['title'].lower() == query.lower()
	]
	return filter(filters[filterby], videos)

def fix_buggy_xml(rawxml):
	"""Fixing the buggy XML, that tape.tv delivers"""
	for old, new in [('<url>','<url><![CDATA['), ('</url>',']]></url>'), ('<image>','<image><![CDATA['), ('</image>',']]></image>')]:
		rawxml = rawxml.replace(old, new)
	return rawxml

def streaminfo(video_id):
	"""Get informations about the stream for the video,which has the id video_id.
	
	Returns a dictionary which has these keys:
	'url', 'token', 'image', 'artist', 'title'
	If no informaton was found, None will be returned"""
	
	if not isinstance(video_id, int):
		try:
			video_id = int(video_id)
		except:
			raise TypeError('video_id must be an integer.')
	
	results = _download_and_parse_xml(
		'http://www.tape.tv/tapeMVC/tape/search/play',
		[
			('telly', 'tapetv'),
			('videoId', video_id)
			
		],
		fix_buggy_xml
	)
	
	if results == None:
		return None
	
	# searching correct entry
	for pl_elem in list(results.find('playlist')):
		if pl_elem.tag != 'video':
			continue
		else:
			try:
				if pl_elem.get('id') == str(video_id):
					url_tmp = pl_elem.find('url').text
					url_tmp = 'mp4:tapetv' + url_tmp[len('tape.tv')+url_tmp.find('tape.tv'):]
					return {
						'url':    url_tmp,
						'token':  pl_elem.find('streamToken').text,
						'image':  pl_elem.find('image').text,
						'artist': pl_elem.find('artist').text,
						'title':  pl_elem.find('title').text
					}
			except:
				continue
	# If we got this far, the correct video was not found, so:
	return None

