from . import *
import datetime
import pickle

TELL_STORE = "TellStore.pkl"
TELL_CACHE = {}

def start():
    global TELL_CACHE
    try:
        TELL_CACHE = pickle.load(file(TELL_STORE))
        print "loaded", TELL_CACHE
    except:
        TELL_CACHE = {}

def stop():
    pickle.dump(TELL_CACHE, file(TELL_STORE, "w"))

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

@command("tell")
def set_tell(who, what, where):
    if " " not in what:
        return

    nick, msg = what.split(" ", 1)    
    msg_list = TELL_CACHE.get(nick.lower(), [])
    msg_list.append("<%s> %s: %s" % (now(), who, msg))
    TELL_CACHE[nick.lower()] = msg_list

@privmsg
def check_tell(who, what, where):
    msgs = TELL_CACHE.get(who.lower(), [])
    if not msgs:
        return
    say(where, "%s, you have %s message%s" % (
        who,
        len(msgs),
        "." if len(msgs)==1 else "s."
    ))
    for msg in msgs:
        say(where, msg)
    del TELL_CACHE[who]
