from Hook import bindFunction,prefers
from Logging import LogFile
import re


log = LogFile("Sed")
msgHistory = [""]*20
sedRegex = "(?P<delim>[^a-zA-Z])(?P<search>.*?)\\1(?P<replace>.*?)\\1(?P<flags>.*?)(?P<extras>(?:\\1.*)|)$"
replacementColors = [4, 7, 3, 10, 6]


def applySed(searchRE,replace,flags,message,colorNum=0):
    log.debug("applySed:",searchRE.pattern,replace,flags,message,colorNum)

    if "c" in flags:
        colorNum %= len(replacementColors)
        replace = "{C%i}%s{}"%(replacementColors[colorNum],replace)

    if "g" in flags:
        out = searchRE.sub(replace,message,0)#all 
    else:
        out = searchRE.sub(replace,message,1)#once
    
    return out

def findMatch(searchRE):
    global msgHistory
    for msg in msgHistory:
        if searchRE.search(msg):
            log.debug("Found match",msg)
            return msg
    log.debug("No match.")
    return None
    
def compileSearch(search,flags):
    try:
        if "i" in flags:
            return re.compile(search,re.I)
        return re.compile(search)
    except:
        log.exception("exception while compiling re:",search)
        return None # incase of a bad search.

@prefers("Colors")
class Sed:

    @bindFunction(message="!s"+sedRegex)
    def doIt(self,delim,search,replace,flags,extras,response,colorize,target):
        log.debug("Sed matching",delim, search,replace,flags,response,colorize)

        searchRE = compileSearch(search,flags)
        if not searchRE:
            return response.msg(target,"Invalid regex '%s' :("%search)

        line = findMatch(searchRE)
        if not line:
            return response.msg(target,"Couldn't find anything to match that!")


        line = applySed(searchRE,replace,flags,line)# apply primary sed
        
        colorIdx = 1 
        while extras:
            delim,search,replace,flags,extras = re.search(sedRegex,extras).groups()
            log.debug("Sed step:",line,delim,search,replace,flags,extras)
            
            searchRE = compileSearch(search,flags)
            if not searchRE:
                return response.msg(target,"Invalid regex '%s' :("%search)
            
            if not colorize:
                flags = flags.replace("c","")

            line = applySed(searchRE,replace,flags,line,colorIdx)
            colorIdx += 1

        if colorize:
            line = colorize(line)
        # super-depressing newline bug fix :(
        line = re.sub(r"(\r|\n)", "", line)
        return response.say(target,line)

    @bindFunction(command="PRIVMSG",message="^[^!]")
    def record(self,message):
        global msgHistory
        log.debug("Sed recording.",msgHistory)
        msgHistory=[message]+msgHistory[:-1]
        
