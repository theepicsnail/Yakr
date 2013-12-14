from yakr.plugin_base import *
import urllib2
import urllib
import re

_URL_RE = "(https?://[][A-Za-z0-9\-._~:/?#@!$&'()*+,;=]+%)"
#http://v.gd/create.php?format=simple&url=www.example.com


@privmsg
def shorten(who, what, where):
    res = re.search(_URL_RE, what)
    if not res:
        return

    url = res.group(0)
    if len(url) <= 18:
        return
    try:
        content = urllib2.urlopen("http://is.gd/create.php?format=simple&url={}"
            .format(urllib.quote(url))).read()
        say(where, "<{C3}Shortened{}: {LINK}%s{} >" % content)
    except urllib2.HTTPError as e:
        say(where, e.read())

