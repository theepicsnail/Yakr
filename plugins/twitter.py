from yakr.plugin_base import *
import tweepy

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_KEY = ""
ACCESS_SECRET = ""
CHANNELS = []

execfile("twitter.cfg")

_API = None

def start():
    global _API
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    _API = tweepy.API(auth)

@command("t")
def manual_tweet(who, what, where):
    print who, what, where
    try:
        if _API.update_status(what):
            say(where, "Update {C9}posted")
        else:
            say(where, "Update {C5}failed")
    except tweepy.TweepError as e:
        say(where, "Update {C5}failed{}: " + e.message[0]["message"])

#:snail!snail@airc-BD88CA3C TOPIC #test :changed topic
@match("^[^ ]+ TOPIC (.*?) :(.*)$")
def topic_tweet(groups):
    where,what = groups
    if where in CHANNELS:
        manual_tweet("", where+": "+what, where)

