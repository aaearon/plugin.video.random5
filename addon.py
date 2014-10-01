import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import random

from resources.lib.xbmcjson import XBMC as xbmcjson

__addon__ = xbmcaddon.Addon(id='plugin.video.random5')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')

addon_handle = int(sys.argv[1])

x = xbmcjson("http://localhost/jsonrpc")

def getShows():
    shows = []

    request = x.VideoLibrary.GetTVShows()['result']['tvshows']

    for s in request:
        shows.append(s)

    return shows

def getEpisodes(show):
    episodes = []

    request = x.VideoLibrary.GetEpisodes({"tvshowid": show, "properties": ["title", "file"]})['result']['episodes']

    for e in request:
        episodes.append(e)

    return episodes

def addItemToPlaylist(episode):
    request = x.Playlist.Add({"item": {"file": episode['file']}, "playlistid": 1})

def getRandomEpisodes(number, show):
    episodes = []
    all_episodes = getEpisodes(show)

    #HARDCODED: returns 5 regardless of what number is
    for i in range(5):
        episodes.append(random.choice(all_episodes))

    return episodes

def createPlaylist(shows):
    # Clear the playlist before we add items to it
    request = x.Playlist.Clear({"playlistid": 1})

    for s in shows:
        addItemToPlaylist(s)

def createMenu(shows):
    #Create 'entire library' list item
    li = xbmcgui.ListItem('ALL TV SHOWS', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='show', listitem=li, isFolder=False)

    for s in shows:
        li = xbmcgui.ListItem(s['label'], iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='show', listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

# createMenu(getShows())

reps = getRandomEpisodes(10, 1)
createPlaylist(reps)
x.Player.Open({"item": {"playlistid": 1}})


