from yakr.plugin_base import *
import subprocess

_BOT = "YakrPush"
_CHANNEL = "#test"
_REPO = "Yakr/master"

_UPDATED = set()

def get_changed(change):
    std_out = subprocess.Popen(["git", "diff", change, "--name-only"], stdout=subprocess.PIPE).communicate()[0]
    return std_out.strip().split("\n")

def pull_changes():
    subprocess.call(["git", "pull"])

@match(":{}.*PRIVMSG {} :{} ([^ ]+).*".format(_BOT, _CHANNEL, _REPO))
def on_privmsg(groups):
    change = groups[0]
    for name in get_changed(change):
        _UPDATED.add(name)

@match(":{}.*PART {}".format(_BOT, _CHANNEL))
def on_part(groups):
    plugins = ""
    non_plugins = ""
    for name in _UPDATED:
        if name.startswith("plugins"):
            plugins += " " + ".".join(name[:-3].split("/")[1:])
        else:
            non_plugins += " " + name

    pull_changes()

    if non_plugins:
        say(_CHANNEL, "Files not cycled:" + non_plugins)
    if plugins:
        say(_CHANNEL, "Cycling"+plugins)
        think(":GitHub_Reloader!a@b.c NOTICE dit :cycle" + plugins)
