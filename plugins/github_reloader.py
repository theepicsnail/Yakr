from yakr.plugin_base import *
from time import sleep
import subprocess

_BOT = "YakrPush"
_CHANNEL = "#test"
_REPO = "Yakr/master"
_UPDATED = 0
def pull_changes():
    print "pulling changes"
    subprocess.call(["git", "pull"])

#Count the number of commits made
@match(":{}.*PRIVMSG {} :{} ([^ ]+).*".format(_BOT, _CHANNEL, _REPO))
def on_privmsg(groups):
    global _UPDATED
    change = groups[0]
    _UPDATED += 1

@match(":{}.*PART {}".format(_BOT, _CHANNEL))
def on_part(groups):
    global _UPDATED
    #Get the changes
    pull_changes()

    #See which files changed in the last N commits
    std_out = subprocess.Popen(
        ["git", "diff", "--name-only", "HEAD", "HEAD~%s" % _UPDATED], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    names = std_out.strip().split("\n")

    _UPDATED = 0

    #Figure out which plugins we need to reload
    plugins = ""
    non_plugins = ""
    for name in names:
        if name.startswith("plugins"):
            plugins += " " + ".".join(name[:-3].split("/")[1:])
        else:
            non_plugins += " " + name

    if non_plugins:
        say(_CHANNEL, "Files not cycled:" + non_plugins)

    if plugins:
        say(_CHANNEL, "Cycling"+plugins)
        think(":GitHub_Reloader!a@b.c NOTICE dit :cycle" + plugins)
