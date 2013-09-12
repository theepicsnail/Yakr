from yakr.plugin_base import *
import gdata.youtube
import gdata.youtube.service
import re

_YT_SERVICE = gdata.youtube.service.YouTubeService()


@command("yt")
def yt(who, what, where):
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = what
    query.max_results = 1
    query.orderby = 'relevance'
    query.racy = 'include'
    feed = _YT_SERVICE.YouTubeQuery(query)

    msg = "<{C4}Youtube{}: {B}%s{B} | {LINK}%s{}>" % (
        feed.entry[0].media.title.text,
        feed.entry[0].media.player.url
    )

    say(where, msg)
