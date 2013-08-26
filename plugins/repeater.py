from . import *

@command("repeat")
def repeat(who, what, where):
    say(where, who + " said " + what)


#from Yakr import Bot
#print Bot
#Bot.join("#foo")
#print "after join"
