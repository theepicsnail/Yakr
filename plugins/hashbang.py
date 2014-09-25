from yakr.plugin_base import *
welcome_text = "Welcome to #!. We are a learning and teaching community. In order to maintain a pleasant environment, please refrain from any negative or hateful speech."
znc_message = "You seem to be joining/parting a lot. Please ask one of our admins about a ZNC."
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
