from datetime import datetime, timedelta
from humanize import naturaltime as natime
from yakr.plugin_base import *
import pickle

SEEN_STORE = "SeenStore.pkl"
_SEEN_CACHE = {}
_LAST_SAVED = datetime.now()
PUBLIC_ROOMS = ["#!", "#!social"]

def ready():
    receiveSelfOutput(True)

def start():
    load_seen()

def load_seen():
    global _SEEN_CACHE
    global _LAST_SAVED
    try:
        _SEEN_CACHE = pickle.load(file(SEEN_STORE))
    except:
        _SEEN_CACHE = {}

def save_seen():
    pickle.dump(_SEEN_CACHE, file(SEEN_STORE, "w"))
    _LAST_SAVED = datetime.now()

@privmsg
def saw(who, what, where):
    _SEEN_CACHE[who] = [where, datetime.now()]
    if _LAST_SAVED < datetime.now() - timedelta(minutes=5):
        save_seen()

@command("seen")
def seen(who, what, where):
    target = what
    if target in _SEEN_CACHE:
        seen_where, seen_when = _SEEN_CACHE[target]
        if seen_where in PUBLIC_ROOMS:
            seen_chan = " in {}".format(seen_where)
        else:
            seen_chan = ""

        say(where, who + ": I last saw {}{} {}.".format(target, seen_chan, natime(seen_when)))
    else:
        say(where, who + ": I've not seen that person speak yet.")