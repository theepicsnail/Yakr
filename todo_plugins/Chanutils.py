
#So this is where I plan on putting all the various channel functions that would be nice to have
#as of the writing of this (7/2/10) the only function is that when you invite superbot he 
#joins wherever you invite him \
import thread,socket,subprocess
def ping(bot,target,host):
    def colorTime(time):
        if time < 10:
            return "{C3}"+str(time)+"{}"
        if time < 50:
            return "{C8}"+str(time)+"{}"
        return "{C4}"+str(time)+"{}"
    #n0cproof
    try:
        out = socket.getaddrinfo(host, 1, 0, 0, socket.SOL_TCP)    
        if out:
            ip = out[0][-1][0]
            bot.say(target,"Resolved: %s"%ip)
            startWrite(bot)
            p = subprocess.Popen('ping -c 5 %s'%host, shell=True, stdout=subprocess.PIPE , stderr=subprocess.PIPE)
            out,err = p.communicate()
            lines = out.split("\n")[1:6]
            if not lines[0]:
                bot.say(target,"Host didn't reply :(")
                startWrite(bot)
                return
            getTime = lambda x:float(x.split("=")[-1].split(" ")[0]) 
            avg = lambda x:sum(x)/len(x)
            time = avg(map(getTime,lines))
            bot.say(target,host+"(%s): %s ms"%(ip,colorTime(time)))
        else:
            bot.say(target,"Could not resolve: "+host)
    except Exception as e:
        bot.say(target,"Could not resolve: "+host)
        raise e
    startWrite(bot)
def startWrite(bot):
    bot.transport.doWrite();

def on_INVITE(bot,sender,msg):
    bot.join(msg[1])
def on_PRIVMSG(bot,sender,msg):
    parts = msg[1].split() #["!ping","google.com","&&","rm","-rf"]
    if parts[0]=="!ping" and len(parts)==2:
        print "Pinging:",parts[1],msg[0]
        bot.say(msg[0],"Pinging "+parts[1])
        thread.start_new_thread(ping,(bot,msg[0],parts[1])) #[superbot,"google.com"] i dunno its still shifty
    pass
    if parts[0]=="!choose":
        from random import choice
        m = " ".join(parts[1:])
        pts = m.split(" or ")
        c = choice(pts)
        print pts, c, msg[0]
        bot.say(msg[0],c)
    if parts[0][0]=="@":
        parts = msg[1].split(" ",1)
        bot.say(parts[0][1:],parts[1])
    if parts[0]=="!8":
        from random import choice
        m = ["As I see it, yes","It is certain","It is decidedly so","Most likely","Outlook good","Signs point to yes","Without a doubt","Yes","Yes - definitely","You may rely on it","Reply hazy, try again","Ask again later","Better not tell you now","Cannot predict now","Concentrate and ask again","Don't count on it","My reply is no","My sources say no","Outlook not so good","Very doubtful"]
        c = choice(m)
        bot.say(msg[0],c)
