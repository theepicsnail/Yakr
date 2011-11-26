from Yakr.Action import *

def handle_line(line):
    #unpack the args. This might be doable easier
    prefix,command,args = line["prefix"],line["command"],line["args"]

    if command=="PRIVMSG":
        if args[1].startswith("!repeat "):
            Say(args[0],"<{}>".format(args[1].replace("!repeat ","")))

        if args[1] == "!part":
            Part(args[0])

    if command=="INVITE":
        Join(args[1])

