import time

def createJson(user, date, hour, lang, place_name, place_country, place_type, place_code,
               bounding_box, text, replies=None):

    if replies:
        reply = [createJson(**getTweetDict(tweet)) for tweet in replies]
    else:
        reply = []


    json_dict = {
        "user": user,
        "datetime": {
            "date": date,
            "time": hour
        },
        "lang": lang,
        "text": text.strip(),
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

    return json_dict


def getTweetDict(tweet, replies=None):

    ts = time.strftime('%d-%m-%Y\t%H:%M:%S', time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
    date_elems = ts.strip().split("\t")

    date = date_elems[0]
    hour = date_elems[1]

    if "retweeted_status" in tweet and tweet["retweeted_status"]:
        text = tweet["text"][3:]
    else:
        text = tweet["text"]

    twdict = {
        "user": tweet["user"]["screen_name"],
        "date": date,
        "hour": hour,
        "lang": tweet["lang"],
        "place_name": tweet["place"]["name"] if tweet["place"] else None,
        "place_country": tweet["place"]["country"] if tweet["place"] else None,
        "place_type": tweet["place"]["place_type"] if tweet["place"] else None,
        "place_code": tweet["place"]["country_code"] if tweet["place"] else None,
        "bounding_box": tweet["place"]["bounding_box"] if tweet["place"] else None,
        "text": text,
        "replies": replies
    }

    return twdict