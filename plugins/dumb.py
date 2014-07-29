from yakr.plugin_base import *
import time
import json
import urllib, urllib2

@command("dumb")
def dumb(who, what, where):
    old_ideas = urllib2.urlopen("http://a.pae.st/RE").read()
    old_ideas += "\n" + time.strftime("%D %H:%M:%S") + " <" + who + "> " + what
    url = "http://a.pae.st/RE/L3vuWm11xnpMso5ff32b.json"
    data = json.dumps({ 'd': old_ideas })
    paestresp = urllib2.urlopen( urllib2.Request(url, data, {'Content-Type': 'application/json'}) )
    say(where, "Dumb idea recorded for posterity DORP. (http://a.pae.st/RE)")

