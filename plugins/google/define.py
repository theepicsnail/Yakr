from yakr.plugin_base import *
from yakr.util import unescape
import re
import urllib2
import json
_API_URL = "http://www.google.com/dictionary/json?callback=dict_api.callbacks.id100&sl=en&tl=en&restrict=pr%2Cde&client=te&q="
@command("gd")
def define(who, what, where):
    if what == "":
        say("!gd <term> [number]")
        return

    match = re.search("^(.*?)( [0-9]+|)$", what)
    term, num = match.groups()
    if not num:
        num = 0
    else:
        num = int(num)-1
    if num < 0:
        say(where, "Definitions run from 1 to N")
        #User input is from 1 to N
        #The variable 'num' is from 0 to N-1
        return
    

    url = _API_URL + urllib2.quote(term)
    reply = urllib2.urlopen(url).read()
    try:
        null = None
        db = eval(reply[24:])
    except:
        pass
    results = db[0]["webDefinitions"][0]["entries"]
    if num >= len(results):
        say(where, "Only %s results." % len(results))
        return
    try:
        result = results[num]["terms"][0]["text"]
        definition = unescape(result)
        say(where,
            "<{C3}Google Define{}: %s [{B}%s{} of %s]>" % (
            definition, num + 1, len(results)
        ))
    except:
        import traceback; traceback.print_exc()
