from yakr.plugin_base import *
import os.path
import random
import re
import subprocess
import threading

_ACTIVITY = set()
_MIN_WAIT = 10 * 60
_MAX_WAIT = 60 * 60
timer = None
shutdown = False
LOCAL_FORTUNE = True
YAKR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_FORTUNE_FILE = os.path.join(YAKR_DIR, "fortunes")
FORTUNE_TEMPLATE = "<{C2}Fortune{}> %s"
RANDOM_FORTUNE_TEMPLATE = "<{C2}Random Fortune{}> %s"

def get_fortune():
    cmd = "fortune -s -n 460 all"  # -s is short, -n tells how many characters

    # And if we have a local fortune file, append it.
    if LOCAL_FORTUNE:
        cmd += " " + LOCAL_FORTUNE_FILE

    return re.sub("\s+", " ",
                  subprocess.check_output(cmd.split()))

@command("fortune")
def manual_fortune(who, what, where):
    fortune = get_fortune()
    say(where, FORTUNE_TEMPLATE % fortune)

@command("add_fortune")
@command("addfortune")
@command("afortune")
def add_fortune(who, what, where):
    if LOCAL_FORTUNE:
        with open(LOCAL_FORTUNE_FILE, 'a') as local_file:
            local_file.writelines([what + "\n", "%\n"])
            local_file.flush()

        # Update DB
        strfile_out = subprocess.check_output(["strfile", LOCAL_FORTUNE_FILE])

        # How many fortunes do we have now?
        num_fortunes = re.findall("(\d+) strings", strfile_out)[0]
        say(where, "%s: Added. Local fortune file now has %s fortunes." % (who, num_fortunes))

    else:
        say(where, "%s: Man, I ain't keepin' track a your NON-SENSE! I was told I din have to!" % who)

def ready():
    if LOCAL_FORTUNE:
        local_fortune()

    schedule_fortune()

def stop():
    global shutdown
    shutdown = True
    if timer is not None:
        timer.cancel()

def local_fortune():
    open(LOCAL_FORTUNE_FILE, 'a').close()  # Make sure the file exists.
    subprocess.call(["strfile", LOCAL_FORTUNE_FILE])  # And is the right format.

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
