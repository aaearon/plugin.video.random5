import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.xbmcjson import XBMC as xbmcjson

__addon__ = xbmcaddon.Addon(id='plugin.video.random5')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')

addon_handle = int(sys.argv[1])

title = "Hello World"
text = "This is some text"
time = 5000 #ms

xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, __icon__))

x = xbmcjson("http://localhost/jsonrpc")
# request = x.VideoLibrary.GetTVShows({"properties":["studio", "genre"]})
#request = x.VideoLibrary.GetTVShows()['result']['tvshows']
# request = x.VideoLibrary.GetEpisodes({"tvshowid": 1, "properties": ["title"]})
# request = x.JSONRPC.Ping()
#xbmc.log('%s' % request[0])

def getShows():
    shows = []
    request = x.VideoLibrary.GetTVShows()['result']['tvshows']
    # xbmc.log('%s' % request)
    for s in request:
        shows.append(s)
    # xbmc.log('%s' % len(shows))
    return shows


def createMenu(shows):
    for s in shows:
        li = xbmcgui.ListItem(s['label'], iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='show', listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

createMenu(getShows())


