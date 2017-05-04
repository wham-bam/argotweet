from TwitterKey import accountKey
from urllib import parse
from JsonManager import createJson, getTweetDict

import twitter
import codecs
import json

class TwitterExtractor(object):

    def __init__(self, query):
        self.q = query
        self._auth = twitter.OAuth(
           accountKey["token"],
           accountKey["token_secret"],
           accountKey["api_key"],
           accountKey["api_secret"]
        )
        self.t = twitter.Twitter(auth=self._auth, retry=True)

    def searchTweet(self):

        bin = []
        bin_reply = []
        json_bin = []

        total_tweets = 0
        MAX_TWEETS = 100

        query_results = self.t.search.tweets(q=self.q)
        statuses = query_results["statuses"]

        print("start tweet search with keyword:", self.q)

        while True:

            try:

                for twt in statuses:

                    total_tweets += 1

                    bin.append(twt)

                    tw_replies = []

                    reply_results = self.t.search.tweets(q="@"+twt["user"]["screen_name"])
                    reply_statuses = reply_results["statuses"]

                    for reply_tweet in reply_statuses:

                        total_tweets += 1

                        if "in_reply_to_status_id" in reply_tweet and\
                                reply_tweet["in_reply_to_status_id"] == twt["id_str"]:

                            print(reply_tweet)
                            bin_reply.append(reply_tweet)
                            tw_replies.append(reply_tweet)

                    datargs = getTweetDict(twt, tw_replies)
                    json_bin.append(createJson(**datargs))

                next_results = query_results["search_metadata"]["next_results"]

                args = dict(parse.parse_qsl(next_results[1:]))

                query_results = self.t.search.tweets(**args)

                statuses = query_results["statuses"]

                print(total_tweets)


                if total_tweets > MAX_TWEETS:

                    print("saving collected tweets...")

                    with codecs.open("./data_folder/raw_tweets_{0}.txt".format(self.q), "a", "utf-8") as raw_out:

                        for tweet in bin:
                            json.dump(tweet, raw_out, separators="\n")

                    with codecs.open("./data_folder/raw_reply_tweets_{0}.txt".format(self.q), "a",
                                     "utf-8") as reply_out:

                        for tweet in bin_reply:
                            json.dump(tweet, reply_out, separators="\n")

                    with codecs.open("./data_folder/tweets_{0}.txt".format(self.q), "a", "utf-8") as js_out:

                        for tweet in json_bin:
                            json.dump(tweet, js_out, separators="\n")

                    bin = []
                    bin_reply = []
                    json_bin = []
                    total_tweets = 0

                    print("tweets saved")

            except:

                break

if __name__ == '__main__':

    twtExt = TwitterExtractor("#brexit")
    twtExt.searchTweet()