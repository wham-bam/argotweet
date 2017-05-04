import json

def createJson(user, date_creation, lang, place_name, place_country, place_type, place_code,
               bounding_box, text, replies=None):

    if replies:
        reply = [createJson(**getTweetDict(tweet)) for tweet in replies]
    else:
        reply = []


    json_dict = {
        "user": user,
        "date": date_creation,
        "lang": lang,
        "text": text,
    }

    json_place = {}

    if place_name:
        json_place["name"] = place_name

    if place_country:
        json_place["country"] = place_country

    if place_type:
        json_place["type"] = place_type

    if place_code:
        json_place["postal_code"] = place_code

    if bounding_box:
        json_place["bounding_box"] = bounding_box


    json_dict["place"] = json_place

    json_dict["reply"] = reply


    js_dump = json.dumps(json_dict)

    return js_dump




def getTweetDict(tweet, replies=None):

    twdict = {
        "user": tweet["user"]["screen_name"],
        "date_creation": tweet["created_at"],
        "lang": tweet["lang"],
        "place_name": tweet["place"]["name"] if tweet["place"] else None,
        "place_country": tweet["place"]["country"] if tweet["place"] else None,
        "place_type": tweet["place"]["place_type"] if tweet["place"] else None,
        "place_code": tweet["place"]["country_code"] if tweet["place"] else None,
        "bounding_box": tweet["place"]["bounding_box"] if tweet["place"] else None,
        "text": tweet["text"],
        "replies": replies
    }

    return twdict