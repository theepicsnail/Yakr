from yakr.plugin_base import *
import subprocess
import threading
import random
import re

_ACTIVITY = set()
_MIN_WAIT = 10 * 60
_MAX_WAIT = 60 * 60
timer = None
shutdown = False
FORTUNE_TEMPLATE = "<{C2}Fortune{}> %s"
RANDOM_FORTUNE_TEMPLATE = "<{C2}Random Fortune{}> %s"

def get_fortune():
    return re.sub("\s+", " ", 
        subprocess.check_output(["fortune", "-s"]))

@command("fortune", False)
def manual_fortune(who, what, where):
    fortune = get_fortune()
    say(where, FORTUNE_TEMPLATE % fortune)

def ready():
    schedule_fortune()

def stop():
    global shutdown
    shutdown = True
    if timer is not None:
        timer.cancel()

def schedule_fortune():
    if shutdown:
        return
    global timer
    delay = random.uniform(_MIN_WAIT, _MAX_WAIT)
    timer = threading.Timer(delay, random_fortune)
    timer.start()

def random_fortune():
    global _ACTIVITY
    schedule_fortune()
    if not _ACTIVITY:
        return

    fortune = get_fortune()

    for channel in _ACTIVITY:
        say(channel, RANDOM_FORTUNE_TEMPLATE % fortune)
    _ACTIVITY = set()

@privmsg
def on_activity(who, what, where):
    global _ACTIVITY
    if where.startswith("#"):
        _ACTIVITY.add(where)
#from Yakr import Bot
#print Bot
#Bot.join("#foo")
#print "after join"
