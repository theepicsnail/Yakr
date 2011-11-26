from Yakr.Action import *
from Yakr.Logger import logger
logger.debug("Inside plugin.")
def handle_line(line):
    prefix,command,args = line["prefix"],line["command"],line["args"]

    if command=="PRIVMSG":
        if args[1].startswith("!repeat"):
            Say(args[0],"<{}>".format(args[1].replace("!repeat","")))
        if args[1] == "!part":
            Part(args[0])
    if command=="INVITE":
        Join(args[1])

