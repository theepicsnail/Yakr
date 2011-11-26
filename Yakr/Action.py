from Logger import logger
bot = None
def Say(channel,msg):
    bot.msg(channel,msg)
def Join(channel):
    bot.cmd("JOIN",channel)
def Part(channel):
    bot.cmd("PART",channel)

