import sys
import xbmc
import xbmcgui
import xbmcplugin
import random
import urlparse
import xbmcaddon

from resources.lib.xbmcjson import XBMC as xbmcjson

__addon__ = xbmcaddon.Addon(id='plugin.video.random5')
__addonname__ = __addon__.getAddonInfo('name')

# Get settings
number = __addon__.getSetting('numberOfEpisodes')
args = urlparse.parse_qs(sys.argv[2][1:])

addon_handle = int(sys.argv[1])
path = args.get('path', None)

x = xbmcjson("http://localhost/jsonrpc")

def log(message, level):
    xbmc.log('[' + __addonname__ + '] ' + message, level)

def getShows():
    shows = []

    request = x.VideoLibrary.GetTVShows()

    for s in request['result']['tvshows']:
        shows.append(s)

    log('Returning %s shows' % len(shows), level=xbmc.LOGDEBUG)
    return shows

def getEpisodes(show):
    show = int(show) # Needs to be an integer
    episodes = []

    request = x.VideoLibrary.GetEpisodes({"tvshowid": show, "properties": ["title", "file"]})

    for e in request['result']['episodes']:
        episodes.append(e)

    log('Returning %s episodes' % len(episodes), level=xbmc.LOGDEBUG)
    return episodes

def addItemToPlaylist(episode):
    request = x.Playlist.Add({"item": {"file": episode['file']}, "playlistid": 1})
    log('Adding %s to playlist' % episode['label'], level=xbmc.LOGDEBUG)

def getRandomEpisodes(number, show):
    number = int(number)
    episodes = []
    all_episodes = getEpisodes(show)

    if (number <= len(all_episodes)):
        for i in range(number):
            episode = random.choice(all_episodes)
            episodes.append(episode)
            log('Randomly chose %s' % episode['label'], level=xbmc.LOGDEBUG)
    elif (number > len(all_episodes)):
        for i in range(len(all_episodes)):
            episode = random.choice(all_episodes)
            episodes.append(episode)
            log('Randomly chose %s' % episode['label'], level=xbmc.LOGDEBUG)

    return episodes

def createPlaylist(shows):
    # Clear the playlist before we add items to it
    request = x.Playlist.Clear({"playlistid": 1})

    for s in shows:
        addItemToPlaylist(s)

    log('Playlist created', level=xbmc.LOGDEBUG)

def createAndPlay(show):
    episodes = getRandomEpisodes(number, show)
    createPlaylist(episodes)
    #x.Player.Open({"item": {"playlistid": 1}})

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