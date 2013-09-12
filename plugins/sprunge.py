from . import *
import urllib, urllib2

_WHERE = ""
_DATA = ""
_LINES = 0
@command("record")
def record(who, what, where):
    global _DATA, _LINES, _WHERE
    _LINES = 10
    if what != "":
        _LINES = int(what)
    
    _LINES = max(1, min(50, _LINES))
    say(where, "Recording {C6}%s{} lines of irc data." % _LINES)
    _DATA = ""
    _WHERE = where


@match("(.*)")
def on_line(groups):
    print _LINES, _DATA, groups
    global _LINES, _DATA
    if _LINES == 0:
        return

    line = groups[0]
    _LINES -= 1
    _DATA += "\n" + line

    if _LINES == 0:
        url = sprunge(_DATA)
        say(_WHERE, url)
        _DATA = ""

def sprunge(data):
    url_data = urllib.urlencode({"sprunge": data})
    return urllib2.urlopen(
        urllib2.Request(
            "http://sprunge.us",
            url_data
        )
    ).read().strip()

