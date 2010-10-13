#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib, urllib2
import xml.etree.ElementTree as etree

def _download_and_parse_xml(url, params):
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
	
		# ...and parse!
		return etree.fromstring(rawxml)
	except:
		return None

def search(query):
	"""Searching music videos in the tape.tv database.
	
	query -- Search for this
	
	
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
	
	return videos

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
			
		]
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

if __name__ == '__main__':
	print streaminfo(search('beck')[0]['id'])
