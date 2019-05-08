# -*- coding: utf-8 -*-
import json
import libmediathek3 as libMediathek

langs = ['de', 'fr']

setting = libMediathek.getSetting
language = langs[int(setting("lang"))]

opa_token = {"Authorization": "Bearer Nzc1Yjc1ZjJkYjk1NWFhN2I2MWEwMmRlMzAzNjI5NmU3NWU3ODg4ODJjOWMxNTMxYzEzZGRjYjg2ZGE4MmIwOA"}
emac_token = {"Authorization": "Bearer MWZmZjk5NjE1ODgxM2E0MTI2NzY4MzQ5MTZkOWVkYTA1M2U4YjM3NDM2MjEwMDllODRhMjIzZjQwNjBiNGYxYw"}

opa_url = 'https://api.arte.tv/api/opa/v3/'
emac_url = 'https://api.arte.tv/api/emac/v3/' + language + '/web'
stream_params = '&quality=$in:XQ,HQ,SQ&mediaType=hls&language=' + language + '&channel=' + language.upper()
	
	
def getDate(yyyymmdd):
	# this would be the better endpoint, but it's not working: /zones/listing_TV_GUIDE?day=
	response = libMediathek.getUrl(emac_url + '/TV_GUIDE?day=' + yyyymmdd, emac_token)
	j = json.loads(response)
	return _parse_data(j['zones'][1]['data'], None, audio_desc='')


def getSearch(s):
	l = []
	url = emac_url + '/zones/listing_SEARCH?limit=20&query=' + s
	return getListings(url)


def getCategories():
	l = []
	response = libMediathek.getUrl(opa_url + 'categories?language=' + language, headers=opa_token)
	j = json.loads(response)
	for category in j['categories']:
		d = {}
		d['_name'] = category['label']
		d['_plot'] = category['description']
		d['mode'] = 'libArteSubcategories'
		d['_type'] = 'dir'
		d['parentCategory'] = category['code']
		d['subcategories'] = json.dumps(category['subcategories'])
		l.append(d)
	return l


def getSubcategories(sublist):
	l = []
	subcategories = json.loads(sublist)
	for subcategory in subcategories:
		d = {}
		d['_name'] = subcategory['label']
		d['_plot'] = subcategory['description']
		d['url'] = opa_url + '/videos?language=' + language + '&subcategory.code=' + subcategory['code']
		d['_type'] = 'dir'
		d['mode'] = 'libArteListVideosNew'
		l.append(d)
	return l


def getCollection(url):
	response = libMediathek.getUrl(url, opa_token)
	j = json.loads(response)
	program_id = j['programs'][0]['programId']

	topic_children = filter(lambda item: item['kind'] == 'TOPIC', j['programs'][0]['children'])
	if topic_children:
		l = [{'_name': 'Übersicht', '_type': 'dir', 'mode': 'libArteListListings', 'url': emac_url + '/zones/collection_videos?id=' + program_id}]
	else:
		return getListings(emac_url + '/zones/collection_videos?id=' + program_id)
	for child in topic_children:
		subresponse = libMediathek.getUrl(opa_url + '/programs?programId=' + child['programId'] + '&language=' + language + '&fields=title,subtitle,fullDescription,shortDescription,mainImage.url', headers=opa_token)
		child_json = json.loads(subresponse)
		program = child_json['programs'][0]
		d = {}
		if program['subtitle'] != None and program['title'] != None:
			d['_name'] = program['title'] + ' | ' + program['subtitle']
		elif program['subtitle'] != None:
			d['_name'] = program['subtitle']
		else:
			d['_name'] = program['title']
		if program['fullDescription']:
			d['_plot'] = program['fullDescription']
		elif program['shortDescription']:
			d['_plot'] = program['shortDescription']
		d['_thumb'] = program['mainImage']['url']
		d['_type'] = 'dir'
		d['mode'] = 'libArteListListings'
		d['url'] = emac_url + '/zones/collection_subcollection?id=' + program_id + '_' + child['programId']
		l.append(d)
	return l


def getListings(url, audio_desc=''):
	l = []
	response = libMediathek.getUrl(url, headers=emac_token)
	j = json.loads(response)
	return _parse_data(j['data'], j['nextPage'], audio_desc=audio_desc)


def _parse_data(data, nextpage, audio_desc=''):
	l = []
	for video in filter(lambda item: item['programId'] is not None, data):
		d = {}
		if video['subtitle'] is not None and video['title'] is not None:
			d['_name'] = video['title'] + ' | ' + video['subtitle']
		elif video['subtitle'] is not None:
			d['_name'] = video['subtitle']
		else:
			d['_name'] = video['title']
		if 'fullDescription' in video and video['fullDescription']:
			d['_plot'] = video['fullDescription']
		elif 'description' in video and video['description']:
			d['_plot'] = video['description']
		elif video['shortDescription']:
			d['_plot'] = video['shortDescription']
		if 'broadcastDates' in video:
			d['_airedtime'] = video['broadcastDates'][0][11:-4]
		if video['images']['landscape']:
			max_res = max(video['images']['landscape']['resolutions'], key=lambda item: item['w'])
			d['_thumb'] = max_res['url']
		elif video['images']['portrait']:
			max_res = max(video['images']['portrait']['resolutions'], key=lambda item: item['h'])
			d['_thumb'] = max_res['url']
		if video['kind']['isCollection']:
			d['mode'] = 'libArteListCollections'
			d['url'] = opa_url + '/programs?programId=' + video['programId'] + '&language=' + language + '&fields=children,programId'
			d['_type'] = 'dir'
		else:
			d['url'] = opa_url + '/videoStreams?programId=' + video['programId'] + stream_params + '&kind=' + video['kind']['code']
			d['mode'] = 'libArtePlay'
			d['_type'] = 'date'
			d['_duration'] = video['duration']
		d['audioDesc'] = audio_desc
		l.append(d)
	if nextpage:
		d = {}
		d['url'] = nextpage
		d['_type'] = 'nextPage'
		d['mode'] = 'libArteListListings'
		if bool(audio_desc):
			d['audioDesc'] = 'True'
		l.append(d)
	return l


def getVideos(url):
	l = []
	response = libMediathek.getUrl(url, headers=opa_token)
	j = json.loads(response)
	for video in j['videos']:
		d = {}
		if video['subtitle'] != None and video['title'] != None:
			d['_name'] = video['title'] + ' | ' + video['subtitle']
		elif video['subtitle'] != None:
			d['_name'] = video['subtitle']
		else:
			d['_name'] = video['title']

		d['_tvshowtitle'] = video['title']
		if video['mainImage']['url'] != None:
			d['_thumb'] = video['mainImage']['url']
		if video['durationSeconds'] != None:
			d['_duration'] = str(video['durationSeconds'])
		if video['teaserText'] != None:
			d['_plotoutline'] = video['teaserText']
			d['_plot'] = video['teaserText']
		if video['fullDescription'] != None:
			d['_plot'] = video['fullDescription']
		elif video['shortDescription'] != None:
			d['_plot'] = video['shortDescription']
		d['url'] = video['links']['videoStreams']['href'] + stream_params
		d['mode'] = 'libArtePlay'
		d['_type'] = 'date'
		l.append(d)
	if j['meta']['videos']['page'] < j['meta']['videos']['pages']:
		d = {}
		d['url'] = j['meta']['videos']['links']['next']['href']
		d['_type'] = 'nextPage'
		d['mode'] = 'libArteListVideosNew'
		l.append(d)
	return l

lang_codes = {
	'de': ['VA', 'VOA'],
	'deSub': ['VOA-STA', 'VA-STA'],
	'deDesc': 'VAAUD',
	'fr': ['VF', 'VOF'],
	'frSub': ['VF-STF', 'VOF-STF'],
	'frDesc': 'VFAUD'
}


def getVideoStream(url, audio_desc=''):
	response = libMediathek.getUrl(url, headers=opa_token)
	j = json.loads(response)
	d = {'media': [], 'metadata': {}}
	result = {'type': 'video', 'stream': 'HLS'}
	fallback_sub = {'type': 'video', 'stream': 'HLS'}
	fallback = {'type': 'video', 'stream': 'HLS'}
	for stream in j['videoStreams']:
		audio_code = stream['audioCode']
		if bool(audio_desc) and audio_code == lang_codes[language + 'Desc']:
			result['url'] = stream['url']
			d['metadata']['duration'] = stream['durationSeconds']
		if audio_code in lang_codes[language] and 'url' not in result:
			result['url'] = stream['url']
			d['metadata']['duration'] = stream['durationSeconds']
		if audio_code in lang_codes[language + 'Sub']:
			fallback_sub['url'] = stream['url']
			d['metadata']['duration'] = stream['durationSeconds']
		if 'url' not in fallback_sub and 'STA' in audio_code:
			fallback_sub['url'] = stream['url']
			d['metadata']['duration'] = stream['durationSeconds']
		if 'VO' in audio_code:
			fallback['url'] = stream['url']
			d['metadata']['duration'] = stream['durationSeconds']
	if 'url' in result:
		d['media'].append(result)
	elif not 'url' in result and 'url' in fallback_sub:
		d['media'].append(fallback_sub)
	else:
		d['media'].append(fallback)
	return d


preferences = {
				'ignore':0,
				'FR':1,
				'OV':2,
				'OMU':3,
				'DE':4,}
	
languages = {
				'FR':'FR',
				'OMU':'DE',
				'DE':'DE'}
				
bitrates = {
				'EQ':800,
				'HQ':1500,
				'SQ':2200,}
	
#legend:
#
#VO Original Voice	
#VOA Original Voice	Allemande
#VOF Original Voice Francaise
#VA Voice Allemande
#VF Voice Francaise
#VAAUD Audio Description Allemande
#VFAUD Audio Description Francaise
#VE* Other Voice
#
#STA Subtitle Allemande
#STF Subtitle Francaise
#STE* Subtitle Other
#STMA Subtitle Mute Allemande
#STMF Subtitle Mute Francaise
#
#* is always followed by the provided language
#[ANG] English
#[ESP] Spanish
#[POL] Polish
#
#examples:
#VOF-STE[ANG] original audio (french), english subtitles
#VOA-STMA orignal audio (german), with french mute sutitles

lang = {
		'VO':'ov',
		'OmU':'ov',
		'VA':'de',
		'VF':'fr',
		'VA-STA':'de',
		'VF-STF':'fr',
		
		'VOA':'de',
		'VOF':'fr',
		'VOA-STA':'omu',
		'VOA-STE':'omu',
		'VOF-STA':'omu',
		'VOF-STE':'omu',
		'VO-STA': 'omu',
		'VAAUD':'de',
		'VFAUD':'fr',
		'VE[ANG]':'en',
		'VE[ESP]':'es',
		'VE[POL]':'pl',
		
		'STA':'de',
		'STF':'fr',
		'STMA':'de',
		'STMF':'fr',
		'STE[ANG]':'en',
		'STE[ESP]':'es',
		'STE[POL]':'pl',
}
