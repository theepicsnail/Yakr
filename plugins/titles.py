from . import *
import urllib2
import re
from yakr.util import unescape
_URL_RE = "(https?[^\s]*)"

@privmsg
def title(who, what, where):
    res = re.search(_URL_RE, what)
    if not res:
        return
    url = res.group(0)

    content = urllib2.urlopen(url, None, 5).read(4096)
    if content.find("</title>") == -1:
        return
    title_content = content.split("</title>")[0].split(">")[-1]
    title_content = re.sub("\W+", " ", title_content) #clean up whitespace

    title = unescape(title_content)

    say(where, "<{B}Title{}: {C7}%s{}>" % title)

