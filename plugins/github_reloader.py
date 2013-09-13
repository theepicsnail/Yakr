from yakr.plugin_base import *
import subprocess

_BOT = "YakrPush"
_CHANNEL = "#test"
_REPO = "Yakr/master"

_UPDATED = set()

def get_changed(change):
    std_out = subprocess.Popen(["git", "diff", change, "--name-only"], stdout=subprocess.PIPE).communicate()[0]
    return std_out.strip().split("\n")

# GitHubPush | Yakr/master 5b3adfc Steven: Fixed the google plugins to refer to yakr.plugin_base
@match(":{}.*PRIVMSG {} :{} ([^ ]+).*".format(_BOT, _CHANNEL, _REPO))
def on_privmsg(groups):
    change = groups[0]
#['main.py', 'plugins/google/define.py', 'plugins/google/search.py', 'plugins/google/youtube.py', 'plugins/joiner.py', 'plugins/maths.py', 'yakr.cfg']
#['main.py', 'plugins/google/define.py', 'plugins/google/search.py', 'plugins/google/youtube.py', 'plugins/joiner.py', 'yakr.cfg']
#['main.py', 'plugins/joiner.py', 'yakr.cfg']
    for name in get_changed(change):
        _UPDATED.add(name)
#    say(where, str(get_changed(change)))

@match(":{}.*PART {}".format(_BOT, _CHANNEL))
def on_part(groups):
    plugins = ""
    non_plugins = ""
    for name in _UPDATED:
        if name.startswith("plugins"):
            plugins += " " + ".".join(name[:-3].split("/")[1:])
        else:
            non_plugins += " " + name
    if plugins:
        think(":GitHub_Reloader!a@b.c NOTICE dit :cycle" + plugins)
        say(_CHANNEL, "Cycling"+plugins)
    if non_plugins:
        say(_CHANNEL, "Files not cycled:" + non_plugins)
#:snail!snail@airc-BD88CA3C NOTICE dit :cycle foo bar baz 
