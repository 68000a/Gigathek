﻿# -*- coding: utf-8 -*-
import xbmcgui
import libmediathek3 as libMediathek
from libdaserste import list

if list() == False:
	dialog = xbmcgui.Dialog()
	title = 'Das Erste Mediathek'
	text = libMediathek.getTranslation(31043)
	dialog.ok(title, text)
