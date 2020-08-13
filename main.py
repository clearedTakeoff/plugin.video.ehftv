import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json
import creds
import os

_url = sys.argv[0]
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_profile = xbmc.translatePath( _addon.getAddonInfo('profile').decode("utf-8"))


def get_url(**kwargs):
    return "{0}?{1}".format(_url, urlencode(kwargs))


def get_categories():
    # Get categories
    return ["Live", "Archive"]

def get_subcategory(category):
    if category == "Live":
        return ["Nothing here at the moment"]
    elif category == "Archive":
        return ["EHF Champions League Men", "EHF Champions League Women", "Men's EHF Euro", "Women's EHF Euro","EHF European League Men", 
        "EHF European League Women", "EHF European Cup Men", "EHF European Cup Women", "Men's Beach Handball EURO", "Women's Beach Handball EURO"]


def get_videos(category, page=0):
    # Find available videos and parse data
    url = "https://ehf-cm.streamamg.com/api/v1/cb6b9d25-5ab3-467a-a5b7-a662b0ddcb3d/BH9t1g7ARQzD2TgcHm9ZosHSES3ADnSpMv60i4pfRqtcti2MeM/\
        30b60d3d-7c68-4215-8b5c-b68ef503980f/en/feed/a9364863-def1-4be6-83c1-c91a632b66a4/sections//search?section=3002115e-7aa8-4ecb-\
            8485-4146612af205&query=(metaData.competition:(" + category + ")%20AND%20metaData.category:(Full%20games))&pageIndex=" + str(page) + "&pageSize=24"
    result = json.loads(requests.get(url).content)
    games = []
    i = 0
    for entry in result["sections"][0]["itemData"]:
        #if entry["metaData"]["body"] is not None:
        body = entry["metaData"]["body"]
        legacy_date = entry["metaData"]["legacy_date"]
        new_entry = {
            "name": body if body is not None else " - ".join(entry["metaData"]["teams"]),
            "video_id": entry["mediaData"]["entryId"],
            "date": legacy_date if legacy_date is not None else entry["publicationData"]["releaseFrom"],
            "thumbnail": entry["mediaData"]["thumbnailUrl"] + "width/600",
            "genre": category
        }
        games.append(new_entry)
    return games


def list_subcategory(category):
    # List subcategory items (competitions under archive section)
    xbmcplugin.setPluginCategory(_handle, str(category))
    xbmcplugin.setContent(_handle, "videos")
    subcategories = get_subcategory(category)
    for s in subcategories:
        list_item = xbmcgui.ListItem(label=s)
        # Maybe add thumbnails?
        list_item.setInfo("video", {"title": s, "mediatype": "video"})
        url = get_url(action="listing", category=s, page=0)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_categories():
    # List the main categories (live and archive)
    xbmcplugin.setPluginCategory(_handle, "Home page")
    xbmcplugin.setContent(_handle, "videos")
    categories = get_categories()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        # TODO: list_item.setArt()...
        list_item.setInfo("video", {"title": category,
                                    "genre": category,
                                    "mediatype": "video"})
        # TODO: More accurate info
        # Recursion: plugin://plugin.video.ehftv/?action=listing&category=archive
        url = get_url(action="sublisting", category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category, page=0):
    # List available videos of a category
    xbmcplugin.setPluginCategory(_handle, category)
    xbmcplugin.setContent(_handle, "videos")
    videos = get_videos(category, page)
    for video in videos:
        y, m, d = video["date"].split("T")[0].split("-")
        date_string = d + "." + m + "." + y
        list_item = xbmcgui.ListItem(label=video["name"] + " (" + date_string + ")", thumbnailImage=video["thumbnail"])
        #list_item.setInfo("general", {"date": d + "." + m + "." + "y"})
        list_item.setInfo("video", {"title": video["name"],
                                    "genre": video["genre"],
                                    "premiered": video["date"].split("T")[0],
                                    "mediatype": "video"})
        list_item.setProperty("IsPlayable", "true")
        # TODO: Add thumbnails, more info...
        url = get_url(action="play", video=video["video_id"])
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    list_item = xbmcgui.ListItem(label="Next page")
    list_item.setInfo("video", {"title": "Next page"})
    url = get_url(action="listing", category=category, page=int(page) + 1)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def obtainKSCookie(content_id, session_cookie):
    xbmcgui.Dialog().ok("Test", "Getting KS cookie")
    url = "https://ehfpayments.streamamg.com/api/v1/session/ksession/?lang=en&entryId=" + content_id + "&apisessionid=" + session_cookie
    user_data = json.loads(requests.get(url).content)
    if user_data["KSession"] is None:
        raise ValueError
    return user_data["KSession"]

def play_video(path):
    # This executes after selecting the stream/video
    # path = id string of the selected video
    try:
        # Try to read session cookie from file on disk
        f = open(_profile + "cookie.secret", "r")
        session_cookie = f.read()
        f.close()
    except IOError:
        # If it doesn't exist user has not been authenticated yet, so do it now
        session_cookie = authenticate()
    try:
        # Try obtaining KS with old session cookie
        ks = obtainKSCookie(path, session_cookie)
    except:
        # If unable, then it probably expired so authenticate again
        session_cookie = authenticate()
        ks = obtainKSCookie(path, session_cookie)
    if ks is None:
        # If we still didn't get KS then credentials are probably wrong
        xbmcgui.Dialog().ok("Something went wrong", "Could not authenticate the user. Check your email and password")
        return
    # Build link to the playlist and pass it to the player
    play_item = xbmcgui.ListItem(path="https://open.http.mp.streamamg.com/p/3001394/sp/300139400/playManifest/entryId/" + path + "/format/applehttp/protocol/https/a.m3u8?ks=" + ks)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def authenticate():
    xbmcgui.Dialog().ok("Test", "Authenticating")
    # Authenticate the user and return user"s cookie
    url = "https://ehfpayments.streamamg.com/api/v1/session/start/?lang=en"
    payload = {"emailaddress": creds.username, "password": creds.password}
    resp = json.loads(requests.post(url, json=payload).content)
    if not os.path.exists(_profile):
        os.makedirs(_profile)
    f = open(_profile + "cookie.secret", "w")
    f.write(resp["CurrentCustomerSession"]["Id"])
    f.close()
    return resp["CurrentCustomerSession"]["Id"]

def router(paramstring):
    # Parse the parameters and execute functions based on results
    params = dict(parse_qsl(paramstring))
    if params:
        if params["action"] == "listing":
            # List available videos of category
            list_videos(params["category"], params["page"])
        elif params["action"] == "play":
            play_video(params["video"])
        elif params["action"] == "sublisting":
            list_subcategory(params["category"])
        else:
            raise ValueError("Invalid paramstring: {0}!".format(paramstring))
    else:
        # On initial startup of the plugin when no parameters are given
        list_categories()


if __name__ == "__main__":
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading "?" from the plugin call paramstring
    router(sys.argv[2][1:])
