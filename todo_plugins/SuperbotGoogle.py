"""
Google plugin for Superbot.
This plugin handles functionality pertaining to google such as
google search, and google weather.

It also doesn't work in places, due to Google changing their search functions. They have an API:
https://code.google.com/apis/customsearch/v1/overview.html
"""

import urllib2, urllib
import simplejson

GOOGLE_AJAX_SEARCH_URL = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&"
GOOGLE_SEARCH_URL = "http://www.google.com/search?&"
GOOGLE_WEATHER_URL = "http://www.google.com/ig/api?"

HEADERS  = {'User-Agent': "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.5)"}

def _buildResponse(url, is_json=False):
    request = urllib2.Request(url, None, HEADERS)
    response = urllib2.urlopen(request)
    if is_json:
        response = simplejson.load(response)
        if not response.has_key('responseData'): return #no data pointless
        return response['responseData']
    return response

def google_search(params):
    """
        Returns google search results(1) for a query.
        @params (dict) contains query value
    """
    url = GOOGLE_AJAX_SEARCH_URL + urllib.urlencode(params)
    response = _buildResponse(url, is_json=True)
    if not response.has_key('results'): return #no results pointless
    results = response['results']
    result = results[0]
    searchstring = "<{C3}Google Search{}: {B}%s{} | {LINK}%s {}>" % (result['titleNoFormatting'], urllib.unquote(result['url']))
    return searchstring

def on_PRIVMSG(bot, sender, args):
    PREFIX = '!'
    nick, channel, args = sender.split('!', 1)[0], args[0], args[1]

    if args.startswith(PREFIX):
        try:
            cmd, msg = args.split(' ', 1)
            if cmd in ["!gs", "!gsearch"]:
                query = {'q': msg}
                bot.say(channel, google_search(query))
            if cmd in ["!gp", "!gspell"]:
                query = {'q': msg}
                bot.say(channel, google_spell(query))
        except ValueError:
            cmd, msg = "", ""


