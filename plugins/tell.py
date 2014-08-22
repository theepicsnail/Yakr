from yakr.plugin_base import *
import datetime
import pickle

TELL_STORE = "TellStore.pkl"
TELL_CACHE = {}

def start():
    global TELL_CACHE
    try:
        TELL_CACHE = pickle.load(file(TELL_STORE))
    except:
        TELL_CACHE = {}

def stop():
    pickle.dump(TELL_CACHE, file(TELL_STORE, "w"))

def now():
    return datetime.datetime.now()

def handler(s, who, what, where):
    if " " not in what:
        return

    nick, msg = what.split(" ", 1)    
    msg_list = TELL_CACHE.get(nick.lower(), [])
    msg_list.append(u"<{}> {}: {}".format(now().strftime("%x %X"), who, msg))
    TELL_CACHE[nick.lower()] = msg_list
    say(where, who + ": I'll make sure to {} {} next time I see them!".format(s, nick))

@command("ask")
def set_ask(who, what, where):
    handler("ask", who, what, where)

@command("tell")
def set_tell(who, what, where):
    if what[-1] == "?":
        handler("ask", who, what, where)
    else:
        handler("tell", who, what, where)

@privmsg
def check_tell(who, what, where):
    msgs = TELL_CACHE.get(who.lower(), [])
    if not msgs:
        return
    msglen = 0
    for msg in msgs:
        msglen += len(msg)
    if (len(msgs) > 4 or msglen > 320) and "#" in where:
        say(where, "{}, I'm gonna deliver your messages via PM to keep from flooding the channel.".format(who))
        where = who
    say(where, "{}, you have {} message{}".format(
        who,
        len(msgs),
        "." if len(msgs)==1 else "s."
    ))
    for msg in msgs:
        say(where, msg)
    del TELL_CACHE[who.lower()]
