from . import *
import shelve
import datetime
import threading

set_command_prefix("\$")
CACHE = None
CHANNEL = "#test"
_DB_FILE = "m528.db"

def restrict_channel(func):
    def nfunc(who, what, where):
        if where != CHANNEL:
            return
        func(who, what, where)
    return nfunc

def start():
    global CACHE
    CACHE = shelve.open(_DB_FILE, writeback = True)

def ready():
    join(CHANNEL)
    auto_update_topic()

def stop():
    CACHE.close()

def get_dt(set_time):
    dt = datetime.datetime.now() - set_time
    return str(dt) 


def auto_update_topic():
    threading.Timer(12*60*60, auto_update_topic)
    update_topic()

_LAST_TOPIC = ""
def update_topic():
    global _LAST_TOPIC
    now = datetime.datetime.now()
    title = ""
    color = 2 
    for nick in CACHE:
        if title:
            title += "{} | "
        color += 1
        if color == 15:
            color = 3
        title += "{C%s}" % color
        title += nick 

        for timer in CACHE[nick]:
            title += " %s:%s" % (
                timer,
                (now - CACHE[nick][timer]).days
            )
    if title == _LAST_TOPIC:
        return
    _LAST_TOPIC = title
    topic(CHANNEL, title)

@command("remove")
@restrict_channel
def remove_stat(who, what, where):
    what = str(what)
    set_time = CACHE.get(who, {}).get(what, None)
    if set_time is None:
        say(where, "You don't have a timer for that!")
        return
    
    say(where, get_dt(set_time))
    del CACHE[who][what]

    if not CACHE[who]:
        del CACHE[who]

    update_topic()

@command("set")
@restrict_channel
def set_stat(who, what, where):
    stat, time = what.split()

    try:
        days = int(time)
    except ValueError:
        say(where, "The syntax for this is $set <timer> <days>.")
        return

    old = CACHE.get(who, {}).get(stat, None)
    if old is not None:
        say(where, get_dt(old))

    d = CACHE.get(who, {})
    d[stat] = datetime.datetime.now() - datetime.timedelta(days)
    CACHE[who] = d
    update_topic()

@command("")
@restrict_channel
def emptyCommand(who, what, where):
    #Handle all of the "$foo" for resetting timers
    if " " in what:
        if what == "":
            say(where, "$<timer> to start a timer, $set <timer> <days> to set it, $remove <timer> to remove it.")
        return
    what = str(what)

    old = CACHE.get(who,{}).get(what,None)
    if old is not None:
        say(where, get_dt(old))

    d = CACHE.get(who, {})
    d[what] = datetime.datetime.now() 
    CACHE[who] = d

    update_topic()
