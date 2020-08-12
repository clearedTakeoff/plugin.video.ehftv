import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import requests
import json

_url = sys.argv[0]
_handle = int(sys.argv[1])


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    # Get categories
    #comps = ["EHF Champions League", "DELO EHF Champions League", "Comps3", "comps4", "Comps5"]
    return ["Live", "Archive"]

def get_subcategory(category):
    if category == "Live":
        return ["Nothing here at the moment"]
    elif category == "Archive":
        # TODO: Get and parse a list of available competitions in archive
        return ["Competition1", "Competition2", "Competition3", "Competition4"]


def get_videos(category):
    # Find available videos and parse data
    url = ""
    result = json.loads(requests.get(url).content)
    games = []
    i = 0
    for entry in result["sections"][0]["itemData"]:
        if entry["metaData"]["body"] is not None:
            new_entry = {
                "name": entry["metaData"]["body"],
                "video": entry["mediaData"]["entryId"],
                "genre": category
            }
            games.append(new_entry)
            # only lists first 10 entries for testing
            i += 1
            if i > 10:
                break
    return games


def list_subcategory(category):
    # List subcategory items (competitions under archive section)
    xbmcplugin.setPluginCategory(_handle, str(category))
    xbmcplugin.setContent(_handle, "videos")
    subcategories = get_subcategory(category)
    for s in subcategories:
        list_item = xbmcgui.ListItem(label=s)
        list_item.setInfo("video", {"title": s, "genre": s, "mediatype": "video"})
        url = get_url(action="listing", category=s)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_categories():
    # List the main categories (live and archive)
    xbmcplugin.setPluginCategory(_handle, 'Home page')
    xbmcplugin.setContent(_handle, 'videos')
    categories = get_categories()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        # TODO: list_item.setArt()...
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # TODO: More accurate info
        # Recursion: plugin://plugin.video.ehftv/?action=listing&category=archive
        url = get_url(action='sublisting', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    # List available videos of a category
    xbmcplugin.setPluginCategory(_handle, category)
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(category)
    for video in videos:
        list_item = xbmcgui.ListItem(label=video['name'])
        list_item.setInfo('video', {'title': video['name'],
                                    'genre': video['genre'],
                                    'mediatype': 'video'})
        list_item.setProperty('IsPlayable', 'true')
        # TODO: Add thumbnails, more info...
        url = get_url(action='play', video=video['video'])
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    # This executes after selecting the stream/video
    # TODO: get stream URL
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    # Parse the parameters and execute functions based on results
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            # List available videos of category
            list_videos(params['category'])
        elif params['action'] == 'play':
            play_video(params['video'])
        elif params["action"] == "sublisting":
            list_subcategory(params["category"])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # On initial startup of the plugin when no parameters are given
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
