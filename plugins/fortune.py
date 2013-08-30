from . import *
import subprocess
import threading
import random
import re

_ACTIVITY = False
_MIN_WAIT = 10 * 60
_MAX_WAIT = 60 * 60
def get_fortune():
    return re.sub("\W+", " ", 
        subprocess.check_output(["fortune", "-s"]))

@command("fortune")
def manual_fortune(who, what, where):
    fortune = get_fortune()
    say(where, "<{C2}Fortune{}> %s" % fortune)

def ready():
    schedule_fortune()

def schedule_fortune():
    threading.Timer(random.randint(_MIN_WAIT, _MAX_WAIT), random_fortune).start()

def random_fortune():
    global _ACTIVITY
    schedule_fortune()
    if not _ACTIVITY:
        return
    _ACTIVITY = False
    fortune = get_fortune()
    say("#adullam", "<{C2}Random Fortune{}> %s" % fortune)

@privmsg
def on_activity(who, what, where):
    global _ACTIVITY
    _ACTIVITY = True
#from Yakr import Bot
#print Bot
#Bot.join("#foo")
#print "after join"
