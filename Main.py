from Yakr.Irc import Bot

if __name__ == '__main__':
    
    SETTINGS = {
        'server': 'udderweb.com', 
        'nick': 'Dot', 
        'realname': 'Dot the bot', 
        'port': 6667, 
        'ssl': False, 
        'channels': ['#test'], 
        'pluginPath': 'Plugins',
        }
    
    bot = Bot(SETTINGS)
    bot.start()
#    jobs = [gevent.spawn(bot.start)]
#    gevent.joinall(jobs)

