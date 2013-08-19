"""Bot"""
from . import *
print("Fortune plugin loaded")

def ready():
    print("fortune ready")
    join("#test")
    say("#test", "hi, i'm a plugin")

#from Yakr import Bot
#print Bot
#Bot.join("#foo")
#print "after join"
