from Hook import *
from Logging import LogFile
try:
    import cPickle as pickle
    log.debug("Using cPickle")
except:
    import pickle
    log.debug("Using pickle")



log = LogFile("Alias")
storeFile = "AliasStore.pkl"
aliases = {}


def saveAliases():
    global aliases
    log.debug("Saving aliases.")
    try:
        pickle.dump(aliases,file(storeFile,"w"))
    except:
        log.exception("Failed to save aliases.")

def loadAliases():
    global aliases
    log.debug("Loading aliases.")
    try:
        aliases = pickle.load(file(storeFile))
        print "Aliases 1:",aliases
        return True
    except:
        log.exception("Failed to load aliases.")
        return False

if not loadAliases():
    saveAliases()
    if not loadAliases():
        log.error("Couldn't load aliases.")

log.dict(aliases,"Loaded Aliases")
print "Aliases 2:",aliases

@requires("IRCArgs")
class Alias:
    @bindFunction(message="^!alias (?P<shorthand>[^ ]+) (?P<expanded>.*)")
    def bindAlias(self, nick, response, shorthand, expanded, target):
        log.debug("Bind",nick, response, shorthand, expanded, target)
        if nick not in aliases:
            aliases[nick]={}
        aliases[nick][shorthand]=expanded
        saveAliases()
   
    @bindFunction(message="^!alias --help")
    def iHelp(self, nick, response, shorthand, target):
        return response.msg(target, "!alias to list your current aliases\n!alias <foo> <bar> to set bar to foo\n!alias -remove <foo> to remove foo\n@foo to use the foo alias")
    
    
    @bindFunction(message="^!alias -h")
    def Help(self, nick, response, shorthand, target):
        return response.msg(target, "!alias to list your current aliases\n!alias <foo> <bar> to set bar to foo\n!alias -remove <foo> to remove foo\n@foo to use the foo alias")
         

    @bindFunction(message="^!alias (?P<shorthand>[^ ]+)$")
    def showAlias(self, nick, response, shorthand, target):
        log.debug("Show", nick, response, shorthand, target)

        expanded = aliases.get(nick,{}).get(shorthand,None)

    @bindFunction(message="^!alias -remove (?P<shorthand>[^ ]+)$")
    def removeAlias(self,nick, response, shorthand, target):
        log.debug("Remove",nick, response, shorthand, target)

        if nick not in aliases:
            return response.msg(target,"You have no aliases assigned.")

        if shorthand not in aliases[nick]:
            return response.msg(target,"You don't have that assigned to anything.")

        aliases[nick].pop(shorthand)
        saveAliases()
        return response.msg(target, shorthand+" removed")

    @bindFunction(message="^@(?P<shorthand>[^ ]+)")
    def errorAlias(self,nick,response,shorthand,target):
        if nick not in aliases:
            return response.msg(target, "You have no aliases set")
        if shorthand not in aliases[nick]:
            return response.msg(target, "No alias set for: "+shorthand)

    @bindFunction(message="@(?P<shorthand>[^ ]+)")
    def runAlias(self, nick, core, event, shorthand):
        log.debug("Run", nick, core, event, shorthand)

        if nick not in aliases:
            log.error(nick,"has no aliases set.")
            return
        if shorthand not in aliases[nick]:
            log.error(nick,"does not have an alias set for:",shorthand)
            return
        event["message"]=event["message"].replace("@%s"%shorthand,aliases[nick][shorthand])
        core.HandleEvent(event) 
        #re-enqueue the event we just got, but with the altered message.

    @bindFunction(message="^!alias$")
    def showAliases(self,response,nick,target):
        log.debug("Show",nick,target)

        if nick not in aliases:
            return response.msg(target,"You have no aliases assigned.")
        msg = ", ".join(aliases[nick].keys())
        return response.msg(target,"Current Aliases:"+msg)

