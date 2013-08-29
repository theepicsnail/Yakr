import gdata.youtube
import gdata.youtube.service
import re

YT_RE = re.compile(r'http://www.youtube.com/watch\?v=([0-9A-Za-z_-]+)')

def YouTubeQuery(query, from_url=False):
    yt_service = gdata.youtube.service.YouTubeService()
    vquery = gdata.youtube.service.YouTubeVideoQuery()
    vquery.vq = query
    vquery.max_results = 1
    vquery.orderby = 'relevance'
    vquery.racy = 'include'
    feed = yt_service.YouTubeQuery(vquery)
    if from_url:
        content = '<{C4}Youtube{}: {B}%s{}>' % (feed.entry[0].media.title.text)
    else:
        content = '<{C4}Youtube{}: {B}%s{B} | {LINK}%s{}>' % (feed.entry[0].media.title.text, feed.entry[0].media.player.url)
    return content        

def on_PRIVMSG(bot, sender, args):
    PREFIX = '!'
    nick, channel, args = sender.split('!', 1)[0], args[0], args[1]
       
    #Handled by URLUtils
    #if YT_RE.search(args):
    #    vid = YT_RE.search(args).groups()[0]
    #    bot.say(channel, YouTubeQuery(vid, from_url=True))
    
    if args.startswith(PREFIX):
        try:
            cmd, msg = args.split(' ', 1)
            if cmd in ['!yt', '!youtube']:
                bot.say(channel, YouTubeQuery(msg))
        except ValueError:
            cmd, msg = "", ""
        
