from yakr.plugin_base import *
welcome_text = "Welcome to #!. We are a learning and teaching community. In order to maintain a pleasant environment, please refrain from any negative or hateful speech."
znc_message = "Bitch, yo shit iz flaky as fuuuuuuk. Get a znc for realz."
_CHANNEL="#!"
diedWithoutTalking = {}

@match("^:(.*?)!.*JOIN :{}".format(_CHANNEL))
def onJoin((name,)):
    notice(name, welcome_text)

    if diedWithoutTalking.get(name, False):
        notice(name, znc_message)
    diedWithoutTalking[name] = True

@match("^:(.*?)!.*PART :{}".format(_CHANNEL))
def onPart((name,)):
    print "part"

@match("^:(.*?)!.*PRIVMSG {} :".format(_CHANNEL))
def onPart((name,)):
    diedWithoutTalking[name] = False
