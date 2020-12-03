import requests
import json
import xbmcgui

# Helper calling suitable get function based on the filter
def filter_videos(filter_condition, value, page):
    # filter: type of filtering (team, competition...)
    # value: name of the competition/team...
    # page: which page
    if filter_condition == "comp":
        return get_videos_category(value, page)
    elif filter_condition == "team":
        return get_videos_team(value, page)
    elif filter_condition == "live":
        return get_live_fixtures()
    #elif filter_condition == "team":
        
def get_live_fixtures():
    url = "https://api.streamplay.streamamg.com/fixtures/handball/p/3001394?q=&offset=0&limit=24"
    result = json.loads(requests.get(url).content)
    games = []
    for entry in result["fixtures"]:
        if len(entry["mediaData"]) > 0 and entry["mediaData"][0]["isLiveUrl"] is not None:
            live_status = json.loads(requests.get(entry["mediaData"][0]["isLiveUrl"]).content)["isLive"]
        else:
            live_status = False
        new_entry = {
            "name": entry["name"],
            "video_id": entry["mediaData"][0]["entryId"] if len(entry["mediaData"]) > 0 else "not_available",
            "date": entry["startDate"],
            "thumbnail": entry["thumbnailFlavors"]["640"],
            "genre": entry["competition"]["name"],
            "live_status": live_status
        }
        games.append(new_entry)
    return games
    

def get_videos_category(category, page=0):
    # Filter available videos by category and parse data
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
    
def get_videos_team(team, page=0):
    # Filter available videos by category and parse data
    url = "https://ehf-cm.streamamg.com/api/v1/cb6b9d25-5ab3-467a-a5b7-a662b0ddcb3d/BH9t1g7ARQzD2TgcHm9ZosHSES3ADnSpMv60i4pfRqtcti2MeM/\
        30b60d3d-7c68-4215-8b5c-b68ef503980f/en/feed/a9364863-def1-4be6-83c1-c91a632b66a4/sections//search?section=3002115e-7aa8-4ecb-\
            8485-4146612af205&query=(metaData.teams:(" + team + ")%20AND%20metaData.category:(Full%20games))&pageIndex=" + str(page) + "&pageSize=24"
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
            "genre": team
        }
        games.append(new_entry)
    if len(games) > 0:
        return games
    else:
        return placeholder()

def placeholder():
    # Placeholder to be used when 0 games available
    return [{"name": "No games found",
            "video_id": "ID_1234",
            "date": "1900-01-01TABC123",
            "thumbnail": None,
            "genre": "team"}]