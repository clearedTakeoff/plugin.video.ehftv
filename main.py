import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import requests
import json
import video_filtering
import os

_url = sys.argv[0]
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_profile = xbmc.translatePath( _addon.getAddonInfo('profile').decode("utf-8"))


def get_url(**kwargs):
    return "{0}?{1}".format(_url, urlencode(kwargs))


def get_categories():
    # Get categories
    return [("Live", "live_listing"), ("Live (Alternate version)", "live_listing_alt"), ("Archive", "sublisting")]

def get_team_list():
    url = "https://wp-ehf.streamamg.com/wp-json/wpa/v1/common_field?slug=common-fields"
    resp = json.loads(requests.get(url).content)
    result = []
    for club in resp["clubs"]:
        result.append((club["sponsor_name"], club["name"].encode("utf-8")))
    return result

def get_comp_list():
    resp = ["EHF Champions League Men", "EHF Champions League Women", "Men's EHF Euro", "Women's EHF Euro","EHF European League Men", 
        "EHF European League Women", "EHF European Cup Men", "EHF European Cup Women", "Men's Beach Handball EURO", "Women's Beach Handball EURO"]
    result = []
    for comp in resp:
        result.append((comp, comp))
    return result

def get_subcategory(category):
    if category == "Live":
        return list_live_videos()
    elif category == "Archive":
        return [("Filter by team", "team"), ("Filter by Competition", "comp"), ("Search", "search")]
    elif category == "comp":
        return get_comp_list()
    elif category == "team":
        return get_team_list()

def list_filtering_options(filter_condition):
    # List possible filtering options items (competitions/teams under archive section)
    xbmcplugin.setPluginCategory(_handle, str(filter_condition))
    xbmcplugin.setContent(_handle, "videos")
    subcategories = get_subcategory(filter_condition)
    for s in subcategories:
        list_item = xbmcgui.ListItem(label=s[0])
        list_item.setInfo("video", {"title": s[0], "mediatype": "video"})
        #xbmc.log("name " + s[1], 2)
        url = get_url(action="listing", filter_condition=filter_condition, value=s[1], page=0)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)

def list_subcategory(category):
    # List subcategory items (competitions under archive section)
    xbmcplugin.setPluginCategory(_handle, str(category))
    xbmcplugin.setContent(_handle, "videos")
    subcategories = get_subcategory(category)
    for s in subcategories:
        list_item = xbmcgui.ListItem(label=s[0])
        list_item.setInfo("video", {"title": s[0], "mediatype": "video"})
        url = get_url(action="filtering", filter_condition=s[1], page=0)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_categories():
    # List the main categories (live and archive)
    xbmcplugin.setPluginCategory(_handle, "Home page")
    xbmcplugin.setContent(_handle, "videos")
    categories = get_categories()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category[0])
        list_item.setInfo("video", {"title": category[0],
                                    "genre": category[0],
                                    "mediatype": "video"})
        # Recursion: plugin://plugin.video.ehftv/?action=listing&category=archive
        url = get_url(action=category[1], category=category[0])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
    list_item = xbmcgui.ListItem(label="Settings")
    list_item.setInfo("video", {"title": "Settings",
                                "genre": "Settings",
                                "mediatype": "video"})
    url = get_url(action="settings")
    is_folder = False
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(filter_condition, value, page=0):
    # List available videos of a category
    xbmcplugin.setPluginCategory(_handle, value)
    xbmcplugin.setContent(_handle, "videos")
    videos = video_filtering.filter_videos(filter_condition, value, page)
    #xbmcgui.Dialog().ok("Testing", "Listing videos??")

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
        # TODO: Make alternate way of playing optional for archive videos too.
        # alt=True fixed for now
        url = get_url(action="play", video=video["video_id"], alt=True)
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    list_item = xbmcgui.ListItem(label="Next page")
    list_item.setInfo("video", {"title": "Next page"})
    url = get_url(action="listing", filter_condition=filter_condition, value=value, page=int(page) + 1)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)
    
def list_live_videos(alt=False):
    # List available videos of a category
    # alt = True - used when m3u8 needs to be saved
    xbmcplugin.setPluginCategory(_handle, "Live matches")
    xbmcplugin.setContent(_handle, "videos")
    videos = video_filtering.filter_videos("live", None, 0)
    for video in videos:
        y, m, d = video["date"].split("T")[0].split("-")
        start_time = video["date"].split("T")[1].split(":")
        date_string = d + "." + m + "." + y
        status = ""
        if video["video_id"] == "not_available":
            status += " - Not available in your region"
        elif video["live_status"] is True:
            status += " - Live now!"
        else:
            status += " - Scheduled"
        list_item = xbmcgui.ListItem(label=video["name"] + " (" + date_string + ")" + status, thumbnailImage=video["thumbnail"])
        list_item.setInfo("video", {"title": video["name"],
                                    "genre": video["genre"],
                                    "premiered": video["date"].split("T")[0],
                                    "mediatype": "video",
                                    "plot": "Starting at " + start_time[0] + ":" + start_time[1] + " GMT"})
        list_item.setProperty("IsPlayable", "true")
        url = get_url(action="play", video=video["video_id"], alt=alt)
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)

def obtainKSCookie(content_id, session_cookie):
    # If there's no session cookie credentials are probably wrong
    if session_cookie is None:
        return None
    url = "https://ehfpayments.streamamg.com/api/v1/session/ksession/?lang=en&entryId=" + content_id + "&apisessionid=" + session_cookie
    user_data = json.loads(requests.get(url).content)
    if user_data["KSession"] is None:
        raise ValueError
    return user_data["KSession"]

def save_modified_m3u8(url):
    req = requests.get(url)
    m3u8 = req.content.decode().split("\n")
    lines_to_remove = []
    for i, line in enumerate(m3u8):
        if ".net:443" in line:
            lines_to_remove.append(i - 1)
            lines_to_remove.append(i)
    lines_to_remove = lines_to_remove[1:]
    m3u8 = [line for i, line in enumerate(m3u8) if i not in lines_to_remove]
    f = open(_profile + "stream.m3u8", "w")
    f.write("\n".join(m3u8))
    f.close()

def play_video(path, alternate=False):
    # If alternate is true it will first download the m3u8 stream and remove the entries containing :443 (maybe useful?)
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
    
    if alternate:
        # Get m3u8 delete lines refering to :443 port and save it
        save_modified_m3u8("https://open.http.mp.streamamg.com/p/3001394/sp/300139400/playManifest/entryId/" + path + "/format/applehttp/protocol/https/a.m3u8?ks=" + ks)
        play_item = xbmcgui.ListItem(path=_profile + "stream.m3u8")
    else:
        # Build link to the playlist and pass it to the player
        play_item = xbmcgui.ListItem(path="https://open.http.mp.streamamg.com/p/3001394/sp/300139400/playManifest/entryId/" + path + "/format/applehttp/protocol/https/a.m3u8?ks=" + ks)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def authenticate():
    # Authenticate the user and return user"s cookie
    url = "https://ehfpayments.streamamg.com/api/v1/session/start/?lang=en"
    payload = {"emailaddress": xbmcaddon.Addon().getSetting("username"), "password": xbmcaddon.Addon().getSetting("password")}
    resp = json.loads(requests.post(url, json=payload).content)
    f = open(_profile + "cookie.secret", "w")
    try:
        f.write(resp["CurrentCustomerSession"]["Id"])
        f.close()
        return resp["CurrentCustomerSession"]["Id"]
    except KeyError:
        f.close()
        return None

def router(paramstring):
    # Parse the parameters and execute functions based on results
    params = dict(parse_qsl(paramstring))
    if params:
        if params["action"] == "listing":
            # List available videos of category
            list_videos(params["filter_condition"], params["value"], params["page"])
        elif params["action"] == "play":
            play_video(params["video"], params["alt"])
        elif params["action"] == "live_listing":
            list_live_videos()
        elif params["action"] == "live_listing_alt":
            list_live_videos(True)
        elif params["action"] == "sublisting":
            list_subcategory(params["category"])
        elif params["action"] == "filtering":
            list_filtering_options(params["filter_condition"])
        elif params["action"] == "settings":
            # Open settings dialog to set email and password
            xbmcaddon.Addon().openSettings()
        else:
            raise ValueError("Invalid paramstring: {0}!".format(paramstring))
    else:
        # On initial startup of the plugin when no parameters are given
        list_categories()


if __name__ == "__main__":
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading "?" from the plugin call paramstring
    router(sys.argv[2][1:])
