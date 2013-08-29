from . import *

@command("repeat")
def repeat(who, what, where):
    say(where, who + " said " + what)


last = ""
@privmsg
def check_duplicates(who, what, where):
    global last
    print "check dups", last, what
    if what == last:
        say(where, what)
        last = ""
    else:
        last = what

#from Yakr import Bot
#print Bot
#Bot.join("#foo")
#print "after join"
