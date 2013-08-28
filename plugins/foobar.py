from . import *
def ready():
   receiveSelfOutput(True)

#PRIVMSG #test :snail said foo
@match("^PRIVMSG ([^ ]+) :(.*foo.*)$")
def on_bot_sending_privmsg(groups):
    print "on privmsg:"
    say(groups[0], groups[1].replace("foo", "bar"))
