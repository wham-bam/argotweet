from TwitterKey import accountKey
from urllib import parse
from urllib.error import HTTPError
from JsonManager import createJson, getTweetDict

import twitter
import codecs
import json
import traceback
import sys
import time

class TwitterExtractor(object):

    def __init__(self, query):

        self.q = query
        self.retrieved = []
        self.max_retrieved = 1000
        self.total_retrieved = 1000

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
                    tw_replies = []

                    top_tweet, twt_bin, replies_bin, tw_replies_bin, _ = self.__getReplies(twt)

                    if top_tweet and twt_bin and replies_bin and tw_replies_bin:

                        if self.__checkTweet(top_tweet, self.retrieved) and \
                                self.__checkList(twt_bin, self.retrieved) and \
                                self.__checkList(tw_replies_bin, self.retrieved):

                            bin += twt_bin
                            bin_reply += replies_bin
                            tw_replies += tw_replies_bin

                            global_list = twt_bin + bin_reply + tw_replies_bin
                            for t in global_list:
                                self.retrieved.append(t["text"])

                            datargs = getTweetDict(top_tweet, tw_replies)
                            json_bin.append(createJson(**datargs))

                next_results = query_results["search_metadata"]["next_results"]

                args = dict(parse.parse_qsl(next_results[1:]))

                query_results = self.t.search.tweets(**args)

                statuses = query_results["statuses"]


                if total_tweets > MAX_TWEETS:

                    self.total_retrieved += total_tweets

                    self.__tweetsSaver(bin, bin_reply, json_bin)

                    bin = []
                    bin_reply = []
                    json_bin = []
                    total_tweets = 0

                    if self.total_retrieved > self.max_retrieved:

                        self.total_retrieved = 0
                        self.retrieved = []


            except KeyError:

                self.total_retrieved += total_tweets

                self.__tweetsSaver(bin, bin_reply, json_bin)

                bin = []
                bin_reply = []
                json_bin = []
                total_tweets = 0

                if self.total_retrieved > self.max_retrieved:
                    self.total_retrieved = 0
                    self.retrieved = []

                for i in range(999, 0, -1):
                    time.sleep(1)
                    sys.stdout.write("\r")
                    sys.stdout.write("No more tweets, waiting {:2d} seconds before restart.".format(i))
                    sys.stdout.flush()
                print("")

                query_results = self.t.search.tweets(q=self.q)
                statuses = query_results["statuses"]

            except Exception:

                bin = []
                bin_reply = []
                json_bin = []
                total_tweets = 0

                print(traceback.format_exc(), file=sys.stderr)

                pass


    def __getReplies(self, tweet):

        tweet_bin = []
        reply_bin = []
        tweet_reply_bin = []

        return self.__getRepliesInternal(tweet, tweet_bin, reply_bin, tweet_reply_bin, 0)



    def __getRepliesInternal(self, tweet, tweet_bin, reply_bin, tweet_reply_bin, level):

        if ("in_reply_to_screen_name" not in tweet) or (not tweet["in_reply_to_screen_name"]):

            tweet_bin.append(tweet)
            return tweet, tweet_bin, reply_bin, tweet_reply_bin, level

        else:

            try:

                original_statuses = self.t.statuses.user_timeline(screen_name=tweet["in_reply_to_screen_name"])

                for original_tweet in original_statuses:

                    if ("in_reply_to_status_id_str" in tweet) and \
                            tweet["in_reply_to_status_id_str"] == original_tweet["id_str"]:

                        print("level", level, ":", tweet["text"].strip(), "==>", original_tweet["text"].strip())

                        top_tweet, tweet_bin, reply_bin, tweet_reply_bin, last_level = self.__getRepliesInternal(original_tweet,
                                                                                                            tweet_bin,
                                                                                                            reply_bin,
                                                                                                            tweet_reply_bin,
                                                                                                            level+1)

                        reply_bin.append(tweet)
                        tweet_reply_bin.append(tweet)

                        return top_tweet, tweet_bin, reply_bin, tweet_reply_bin, last_level


                # if no tweet is founded
                return tweet, tweet_bin, reply_bin, tweet_reply_bin, level


            except:

                # if it is not possible to access to a user, return the last tweet and its replies
                return tweet, tweet_bin, reply_bin, tweet_reply_bin, level


    def __tweetsSaver(self, bin, bin_reply, json_bin):

        print("saving collected tweets...")

        with codecs.open("./data_folder/raw_tweets_{0}.txt".format(self.q), "a", "utf-8") as raw_out:

            for tweet in bin:
                json.dump(tweet, raw_out, ensure_ascii=False)
                raw_out.write("\n")

        with codecs.open("./data_folder/raw_reply_tweets_{0}.txt".format(self.q), "a",
                         "utf-8") as reply_out:

            for tweet in bin_reply:
                json.dump(tweet, reply_out, ensure_ascii=False)
                reply_out.write("\n")

        with codecs.open("./data_folder/tweets_{0}.txt".format(self.q), "a", "utf-8") as js_out:

            for tweet in json_bin:
                json.dump(tweet, js_out, ensure_ascii=False)
                js_out.write("\n")

        print("tweets saved")


    def __checkTweet(self, tweet, retrieved_list):

        if tweet["text"] in retrieved_list:
            return False
        return True

    def __checkList(self, twt_list, retrieved_list):

        for twt in twt_list:
            if not self.__checkTweet(twt, retrieved_list):
                return False

        return True

if __name__ == '__main__':

    twtExt = TwitterExtractor("#brexit")
    #twtExt = TwitterExtractor("#trump")
    #twtExt = TwitterExtractor("@realDonaldTrump")
    twtExt.searchTweet()