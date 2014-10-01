import sys
import xbmc
import xbmcgui
import xbmcplugin
import random
import urlparse

from resources.lib.xbmcjson import XBMC as xbmcjson

args = urlparse.parse_qs(sys.argv[2][1:])
addon_handle = int(sys.argv[1])

x = xbmcjson("http://localhost/jsonrpc")

path = args.get('path', None)

def getShows():
    shows = []

    request = x.VideoLibrary.GetTVShows()

    for s in request['result']['tvshows']:
        shows.append(s)

    return shows

def getEpisodes(show):
    show = int(show) # Needs to be an integer
    episodes = []

    request = x.VideoLibrary.GetEpisodes({"tvshowid": show, "properties": ["title", "file"]})

    for e in request['result']['episodes']:
        episodes.append(e)

    return episodes

def addItemToPlaylist(episode):
    request = x.Playlist.Add({"item": {"file": episode['file']}, "playlistid": 1})

def getRandomEpisodes(number, show):
    episodes = []
    all_episodes = getEpisodes(show)

    #HARDCODED: returns 5 regardless of what number is, eventually this will be configurable value
    for i in range(5):
        episodes.append(random.choice(all_episodes))

    return episodes

def createPlaylist(shows):
    # Clear the playlist before we add items to it
    request = x.Playlist.Clear({"playlistid": 1})

    for s in shows:
        addItemToPlaylist(s)

def createAndPlay(show):
    episodes = getRandomEpisodes(5, show)
    createPlaylist(episodes)
    x.Player.Open({"item": {"playlistid": 1}})

def createMenu(shows):
    #Create 'entire library' list item
    # li = xbmcgui.ListItem('ALL TV SHOWS', iconImage='DefaultFolder.png')
    # xbmcplugin.addDirectoryItem(handle=addon_handle, url='show', listitem=li, isFolder=False)

    for s in shows:
        url = sys.argv[0] + "?path=/play&show=%s" % (s['tvshowid'])
        li = xbmcgui.ListItem(s['label'], iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

if path is None:
    createMenu(getShows())

elif path[0] == '/play':
    showid = args.get('show', None)
    createAndPlay(showid[0])


