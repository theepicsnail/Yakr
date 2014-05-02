from yakr.plugin_base import *
from howdoi import howdoi
import re
import urllib, urllib2

@command("howdoi")
def howdo(who, what, where):
    # Get the response from howdoi
    try:
        howresp = howdoi.howdoi({
            'all': False,
            'clear_cache': False,
            'color': False,
            'pos': 1,
            'link': False,
            'query': what.split(),
            'num_answers': 1,})

        # And a link
        howurl = howdoi.howdoi({
            'all': False,
            'clear_cache': False,
            'color': False,
            'pos': 1,
            'link': True,
            'query': what.split(),
            'num_answers': 1,})

    except:
        # Been having it fail on certain queries.
        # "foam babby" is one.

        # Also, 70 just because it makes me happy, alright?
        # http://www.freebsd.org/cgi/man.cgi?query=sysexits
        return 70

    # If it's one line, send it to IRC
    if howresp.count('\n') <= 1:
        msg = who + ": " + howresp

    # Otherwise, pae.st it.
    else:
        if howurl:
            paest = howresp + "\n\nFor more info, check: " + howurl
            data = urllib.urlencode({'d': howresp})
            paestresp = urllib2.urlopen(
                urllib2.Request("http://a.pae.st", data)
            ).read()
            s = re.compile("(http.*)(?:#WEB-PUBLIC)").search(paestresp)
            msg = who + ": Try " + s.groups()[0] + "."
        else:
            msg = who + ": " + howresp

    say(where, msg)
    

@match("^:(.*)!.*PRIVMSG ([^ ]+) :[Hh]ow do [Ii] (.*)")
def howdo2(groups):
    # Capture order *grumble grumble*
    howdo(groups[0], groups[2], groups[1])
