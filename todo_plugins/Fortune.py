import thread,os
from time import sleep
import random

activity = False
loaded=False
def on_load(bot):
    global loaded  
    loaded= True
    thread.start_new_thread(fortuneTimer,(bot,))

def on_unload(bot):
    global loaded
    loaded=False

def fortuneTimer(bot):
    global loaded,activity
    print "FortuneTimer", loaded
    while loaded:
        sleep(random.randrange(10, 60)*60)
        if activity:
            doFortune(bot, random=True)
            activity = False

def on_PRIVMSG(bot,nick,msg):
    global activity
    source = msg[0]
    if source == bot.nickname:
        source = nick.split("!")[0]
    if msg[1]=="!fortune": #bad , quick 
        doFortune(bot)
    activity = True

def doFortune(bot, random=False):
    p = os.popen("fortune -s")
    fortune = p.read()
    fortune = ' '.join(fortune.split()).replace('\n', ' ')
    if random:
        bot.say("#adullam", "<{C2}Random Fortune{}> %s" % fortune)
    else:
        bot.say("#adullam",fortune)

