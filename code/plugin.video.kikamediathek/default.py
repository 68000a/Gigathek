# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import libmediathek3 as libMediathek
import platform

libMediathek.endOfDirectory()
dialog = xbmcgui.Dialog()
title = 'KiKA Mediathek'
text = 'Im Juni 2026 wurde das API der KiKA Mediathek abgeschaltet. Die von der ARD bereitgestellten KiKA Inhalte sind über die ARD-Mediathek abrufbar, die vom ZDF bereitgestellten KiKA Inhalte sind über die ZDF-Mediathek oder über ZDF-Tivi abrufbar.'
text = text + ' [Py' + platform.python_version() + ']'
dialog.ok(title, text)
xbmc.executebuiltin('XBMC.ActivateWindow(Home)')
