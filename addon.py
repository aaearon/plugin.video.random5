import sys
import xbmc
import xbmcgui
import xbmcplugin
import random
import urlparse
import xbmcaddon

from resources.lib.xbmcjson import XBMC as xbmcjson

addon_handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.random5')
__addonname__ = __addon__.getAddonInfo('name')

# Get settings
number = int(__addon__.getSetting('number_of_episodes'))
watched_only = __addon__.getSetting('watched_only')
sequential_order = __addon__.getSetting('sequential_order')
autoplay = __addon__.getSetting('autoplay')
random_show_list_item = __addon__.getSetting('random_show_list_item')

args = urlparse.parse_qs(sys.argv[2][1:])
path = args.get('path', None)

x = xbmcjson("http://localhost/jsonrpc")

def log(message, level):
    xbmc.log('[' + __addonname__ + '] ' + message, level)

def get_shows():
    """Returns all shows in the library"""
    request = x.VideoLibrary.GetTVShows()
    shows = request['result']['tvshows']

    log('Returning %s shows' % len(shows), level=xbmc.LOGDEBUG)
    return shows

def get_episodes_by_show(show):
    """Gets all episodes for given show"""
    show = int(show) # Needs to be an integer

    request = x.VideoLibrary.GetEpisodes({'tvshowid': show, 'properties': ['title', 'file', 'playcount']})
    episodes = request['result']['episodes']

    if watched_only == 'true':
        episodes = get_watched_episodes(episodes)

    log('Returning %s episodes to start with' % len(episodes), level=xbmc.LOGDEBUG)
    return episodes

def add_file_to_playlist(file):
    """Adds a video file to the video playlist"""
    request = x.Playlist.Add({"item": {"file": file['file']}, "playlistid": 1})
    log('Adding %s to playlist' % file['label'], level=xbmc.LOGDEBUG)

def get_watched_episodes(episode_list):
    """Takes a list of episodes and returns only episodes that have a playcount of > 0"""
    watched_episodes = []
    for episode in episode_list:
        if episode['playcount'] > 0:
            watched_episodes.append(episode)

    return watched_episodes

def get_episodes():
    """Returns all episodes"""
    request = x.VideoLibrary.GetEpisodes({'properties': ['title', 'tvshowid', 'file', 'playcount']})
    episodes = request['result']['episodes']

    if watched_only == 'true':
        episodes = get_watched_episodes(episodes)

    return episodes

def get_episode(episode_id):
    """Returns episode with specified episodeid"""
    request = x.VideoLibrary.GetEpisodeDetails({'episodeid': episode_id, 'properties': ['tvshowid', 'file', 'playcount']})
    return request['result']['episodedetails']

def get_sequential_episodes(number, show):
    episodes = []
    show_episodes = get_episodes_by_show(show)

    if len(episodes) < number: # Just start with the first episode
        first_episode = show_episodes[0]
        episodes.append(first_episode)

    else: # Get a random episode from the show and add it to the list
        first_episode = random.choice(show_episodes)
        episodes.append(first_episode)

    # Next episode is the index of the first episode + 1
    next_episode = show_episodes.index(first_episode) + 1

    while len(episodes) < number:
        try:
            episode = show_episodes[next_episode]
            episodes.append(episode)
            next_episode += 1
        except IndexError:
            break

    return episodes

def get_random_episodes(number, show):
    """Randomly selects a number of episodes from a particular show"""
    episodes = []
    all_episodes = get_episodes_by_show(show)

    # Check to make sure we still have an episode pool to pull from
    if len(all_episodes) < 1:
        line1 = 'There are no episodes to create a playlist from!'
        line2 = '\nEither the TV show has no episodes or if watched only is selected, all episodes are unwatched.'
        xbmcgui.Dialog().ok(__addonname__, line1, line2)

    if number <= len(all_episodes):
        while len(episodes) < number:
            random_episode = random.choice(all_episodes)
            if random_episode not in episodes:
                episodes.append(random_episode)
                log('Randomly chose episode %s with playcount %s' % (random_episode['label'], random_episode['playcount']), level=xbmc.LOGDEBUG)

    # If there are not enough episodes to meet the desired number of playlist items, add what episodes there are
    elif number > len(all_episodes):
        while len(episodes) < len(all_episodes):
            random_episode = random.choice(all_episodes)
            if random_episode not in episodes:
                episodes.append(random_episode)
                log('Randomly chose %s with playcount %s' % (random_episode['label'], random_episode['playcount']), level=xbmc.LOGDEBUG)

    return episodes

def create_playlist(episode_list):
    """Creates a playlist of episodes of a particular show"""
    # Clear the playlist before we add items to it
    request = x.Playlist.Clear({"playlistid": 1})

    for item in episode_list:
        add_file_to_playlist(item)

    log('Playlist created', level=xbmc.LOGDEBUG)

def create_and_play(show):
    """Creates playlist and plays playlist"""
    if sequential_order == 'true':
        episodes = get_sequential_episodes(number, show)
    else:
        episodes = get_random_episodes(number, show)

    create_playlist(episodes)

    if autoplay == 'true':
        x.Player.Open({"item": {"playlistid": 1}})
        log('Playing playlist', level=xbmc.LOGDEBUG)
    else:
        x.GUI.ActivateWindow({'window': 'videoplaylist'})
        log('Showing playlist', level=xbmc.LOGDEBUG)

def create_menu(show_list):
    """Creates the 'folder' menu"""

    # TODO: Create 'entire library' list item
    # li = xbmcgui.ListItem('ALL TV SHOWS', iconImage='DefaultFolder.png')
    # xbmcplugin.addDirectoryItem(handle=addon_handle, url='show', listitem=li, isFolder=False)

    # 'Random show' entry
    if random_show_list_item == 'true':
        random_show = random.choice(show_list)
        url = sys.argv[0] + "?path=/play&show=%s" % (random_show['tvshowid'])
        li = xbmcgui.ListItem('- RANDOM SHOW -', iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    for s in show_list:
        url = sys.argv[0] + "?path=/play&show=%s" % (s['tvshowid'])
        li = xbmcgui.ListItem(s['label'], iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle)

# The 'navigation' part
if path is None:
    create_menu(get_shows())

elif path[0] == '/play':
    showid = args.get('show', None)
    create_and_play(showid[0])