# -*- coding: utf-8 -*-
import sys
import libartejsonparser as libArteJsonParser
import libmediathek3 as libMediathek

translation = libMediathek.getTranslation
settings = libMediathek.getSetting
language = libArteJsonParser.language

emac_url = 'https://api.arte.tv/api/emac/v3/' + language + '/web'


def libArteListMain():
	l = []
	l.append({'_name': translation(31031), 'mode': 'libArteListListings',	'_type': 'dir', 'url': emac_url + '/zones/listing_MOST_VIEWED?limit=20'})
	l.append({'_name': translation(31032), 'mode': 'libArteListListings',  	'_type': 'dir', 'url': emac_url + '/zones/magazines_HOME?limit=20'})
	l.append({'_name': translation(31033), 'mode': 'libArteListDate',		'_type':'dir'})
	l.append({'_name': translation(31035), 'mode': 'libArteListListings',		'_type': 'dir', 'url': emac_url + '/zones/playlists_HOME?limit=20'})
	l.append({'_name': translation(31034), 'mode': 'libArteCategories', '_type': 'dir'})
	l.append({'_name': translation(31043), 'mode': 'libArteListListings', '_type': 'dir', 'url': emac_url + '/zones/listing_LAST_CHANCE?limit=20'})
	l.append({'_name': translation(31044), 'mode': 'libArteListListings', '_type': 'dir', 'url': emac_url + '/zones/listing_MOST_RECENT?limit=20'})
	l.append({'_name': translation(31045), 'mode': 'libArteListListings', '_type': 'dir', 'url': emac_url + '/zones/listing_AUDIO_DESCRIPTION?limit=20', 'audioDesc': 'True'})
	l.append({'_name': translation(31046), 'mode': 'libArteListListings', '_type': 'dir', 'url': emac_url + '/zones/highlights_HOME?limit=20'})
	l.append({'_name': translation(31039), 'mode': 'libArteSearch', 		'_type': 'dir'})
	return l

def libArteCategories():
	return libArteJsonParser.getCategories()


def libArteSubcategories():
	return libArteJsonParser.getSubcategories(params['subcategories'])

	
def libArteListVideos():
	return libArteJsonParser.getVideos(params['url'])


def libArteListListings():
	audio_desc = ''
	if 'audioDesc' in params:
		audio_desc = params['audioDesc']
	return libArteJsonParser.getListings(params['url'], audio_desc=audio_desc)


def libArteListCollections():
	return libArteJsonParser.getCollection(params['url'])


def libArteListVideosNew():
	return libArteJsonParser.getVideos(params['url'])


def libArteListDate():
	date_dirs = libMediathek.populateDirDate('libArteListDateVideos', dateChooser=True)
	date_dirs.append({'_name': translation(31046), 'mode': 'libArteListListings', '_type': 'dir', 'url': emac_url + '/zones/highlights_TV_GUIDE?limit=20'})
	return date_dirs


def libArteListDateVideos():
	if 'yyyymmdd' not in params:
		params['yyyymmdd'] = libMediathek.dialogDate('%Y-%m-%d')
	return libArteJsonParser.getDate(params['yyyymmdd'])


def libArteSearch():
	search_string = libMediathek.getSearchString()
	return libArteJsonParser.getSearch(search_string)


def libArtePlay():
	if 'audioDesc' not in params:
		params['audioDesc'] = ''
	return libArteJsonParser.getVideoStream(params['url'], audio_desc=params['audioDesc'])


def headUrl(url):#TODO: move to libmediathek3
	libMediathek.log(url)
	import urllib2
	req = urllib2.Request(url)
	req.get_method = lambda: 'HEAD'
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
	
	response = urllib2.urlopen(req)
	info = response.info()
	response.close()
	return info


def list():	
	modes = {
	'libArteListMain': libArteListMain,
	'libArteCategories': libArteCategories,
	'libArteSubcategories': libArteSubcategories,
	'libArteListVideos': libArteListVideos,
	'libArteListListings': libArteListListings,
	'libArteListCollections': libArteListCollections,
	'libArteListVideosNew': libArteListVideosNew,
	'libArteListDate': libArteListDate,
	'libArteListDateVideos': libArteListDateVideos,
	'libArteSearch': libArteSearch,
	'libArtePlay': libArtePlay,
	}
	
	global params
	params = libMediathek.get_params()
	global pluginhandle
	pluginhandle = int(sys.argv[1])
	mode = params.get('mode','libArteListMain')
	if mode == 'libArtePlay':
		libMediathek.play(libArtePlay())
	else:
		l = modes.get(mode)()
		libMediathek.addEntries(l)
		libMediathek.endOfDirectory()	
