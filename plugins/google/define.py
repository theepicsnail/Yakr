from .. import *
from ..titles import unescape
import re
import urllib2
import json
_API_URL = "http://www.google.com/dictionary/json?callback=dict_api.callbacks.id100&sl=en&tl=en&restrict=pr%2Cde&client=te&q="
@command("gd")
def define(who, what, where):
    match = re.search("^(.*?) ?([0-9]+|)$", what)
    term, num = match.groups()
    if not num:
        num = 1
    else:
        num = int(num)
    if num == 0:
        say(where, "Definitions run from 1 to N")
        return

    url = _API_URL + urllib2.quote(term)
    reply = urllib2.urlopen(url).read()
    try:
        null = None
        db = eval(reply[24:])
    except:
        pass
    results = db[0]["webDefinitions"][0]["entries"]
    if num > len(results):
        say(where, "Only %s results." % num)
        return

    result = results[num-1]["terms"][0]["text"]
    definition = unescape(result)
    say(where,
        "<{C3}Google Define{}: %s [{B}%s{} of %s]>" % (
        definition, num, len(results)     
    ))
