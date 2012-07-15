class BotBase(object):
    def connect(self): 
        raise NotImplementedError("BotBase.connect")
    def quit(self):
        raise NotImplementedError("BotBase.quit")
    def msg(self,target,message):
        raise NotImplementedError("BotBase.msg")
    def me(self,target,message):
        self.msg(target,"\01ACTION "+message+"\01")
    def nick(self,newNick=None):
        raise NotImplementedError("BotBase.nick")
    def join(self,channel):
        raise NotImplementedError("BotBase.join")
    def part(self,channel):
        raise NotImplementedError("BotBase.part")




