import shelve
from datetime import datetime,timedelta
db = None

prefix="$"
channel="#m528"
lastTopic = ""
lastUpdateTime = datetime.now()
updateFrequency = timedelta(0, 43200) # day, seconds---43200 seconds = 12 hours.

def on_load(bot):
    global db
    db = shelve.open("m528.db", writeback=True) #if this causes problems it's not necessary 
    bot.join(channel)
    pass

def on_unload(bot):
    db.close()
    bot.part(channel)
    pass

def on_PING(bot, sender, args):
    global lastUpdateTime, updateFrequency
    if ( datetime.now() - lastUpdateTime > updateFrequency ):
        updateTopic(bot)
        lastUpdateTime = datetime.now()

def updateTopic(bot):#update the topic if necessary
    global lastTopic
    curTopic = genTopic()
    if curTopic != lastTopic:
        print "Topics differ!"
        print "Currently: "+lastTopic
        print "New: "+curTopic
        bot.topic(channel, curTopic)
        lastTopic = curTopic #This isn't sticking :(

def genTopic():
    title=""
    color = 2
    user_prefix = ""
    for user in db.keys():
        privdb = db[user]
        color = color +1 
        if color == 15:
            color = 3
        title+=chr(3)+str(color)+user_prefix+user+" "
        for event in privdb.keys():
            time= str((datetime.now()-privdb[event]).days)
            title+=event+":"+time+" "
#        title+="]"
        user_prefix = "| "
    return title

def on_PRIVMSG(bot, sender, args):
    nick, chan, msg = sender.split('!', 1)[0], args[0], args[1]
    
    update= False
    if chan==channel and msg.startswith(prefix):
        args = msg.split(None,1)

        privdb={}
        if db.has_key(nick):
            privdb=db[nick]

        key = args[0][1:]
        length = None
        timeDelta = None
        if privdb.has_key(key):
            timeDelta = datetime.now()-privdb[key]
            length = timeDelta.days
            timeDelta = str(timeDelta)
            if length!=1:
                length = str(length)+" days"
            else:
                length = str(length)+" day"
                

        if len(args)==1:
            if length:
                bot.say(channel,"Timer reset, length = "+timeDelta)
            else:
                bot.say(channel,"New timer started! Be strong!")

            privdb[key]=datetime.now()
            update = True
        else:
            if args[1]=="remove":
                if length:
                    bot.say(channel,"Timer removed.  length = "+timeDelta)
                    del privdb[key]
                    print privdb,len(privdb)
                    if len(privdb)==0:
                        privdb=None
                    update = True
                else:
                    bot.say(channel,"You never had that timer!")

            elif args[1]=="stat":
                if length:
                    bot.say(channel,timeDelta)
                else:
                    bot.say(channel,"You never started that timer, use "+prefix+key+" to start it!")
            else:
                try:
                    d = int(args[1])
                    length = str(d)+" day"
                    if d!=1:
                        length += "s"
                    td = timedelta(days=d)
                    privdb[key]=datetime.now()-td
                    bot.say(channel,"Timer reset, length = "+timeDelta)
                    update = True
                except:
                    bot.say(channel,"Try: "+prefix+key+" # to set the number of days on your timer")

        if privdb:
            db[nick]=privdb
        else:
            del db[nick]

        if update:
            db.sync() # this will possibly fix superbots amnesia
            updateTopic(bot)
    pass


