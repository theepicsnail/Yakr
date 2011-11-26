from Yakr.Irc import Bot
import sys
SETTINGS = {
    'server': 'udderweb.com', 
    'nick': 'Dot', 
    'realname': 'Dot the bot', 
    'port': 6667, 
    'ssl': False, 
    'channels': ['#test'], 
    'pluginPath': 'Plugins',
    }

if __name__ == '__main__':
    if len(sys.argv)==1:
        bot = Bot(SETTINGS)
        bot.start()
    elif sys.argv[1]=="PluginTest":
        from Yakr.Plugin import PluginManager
        PluginManager(SETTINGS["pluginPath"]).autoload()

#    jobs = [gevent.spawn(bot.start)]
#    gevent.joinall(jobs)

