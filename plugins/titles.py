from . import *
import urllib2
import re
from yakr.util import unescape
_URL_RE = "(https?://[\x20-\x7F]+)"

@privmsg
def title(who, what, where):
    res = re.search(_URL_RE, what)
    if not res:
        return
    url = res.group(0)
    try:
        req = urllib2.Request(url, headers={'User-Agent': 'Yakr'})
        content = urllib2.urlopen(req, timeout=5).read(4096)
    except urllib2.HTTPError as e:
        if e.code == 401:
            say(where, "I don't have login info for that link. No title for you! (401)")
        elif e.code == 403:
            say(where, "That website told me to GTFO (403). ROBOT HATER!")
        elif e.code == 404:
            say(where, "I don't know where you think you're sending people, but that website told me it couldn't find your link. (404)")
        elif e.code == 405:
            say(where, "I'm not supposed to be GETting that link. You're going to get me in trouble, {}! D:< ({})".format(who, e.code))
        elif e.code == 418:
            say(where, "Ooh, a teapot! Thank you for the lovely tea, {}!".format(who))
        else:
            say(where, "I ran into a sort of problem, you see. I dunno what to do! ({}) {}".format(e.code, e.reason))
        return
    except Exception as e:
        say(where, "O.o %r" % e.message )
        return
    if content.find("</title>") == -1:
        return
    title_content = content.split("</title>")[0].split(">")[-1]
    title_content = re.sub("\W+", " ", title_content) #clean up whitespace

    title = unescape(title_content)

    say(where, "<{B}Title{}: {C7}%s{}>" % title)

