from . import *

@command("repeat")
def repeat(who, what, where):
    say(where, what)


last = ""
@privmsg
def check_duplicates(who, what, where):
    global last
    if what == last:
        say(where, what)
        last = ""
    else:
        last = what

#from Yakr import Bot
#print Bot
#Bot.join("#foo")
#print "after join"
