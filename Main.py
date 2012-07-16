from Yakr.Irc import Bot
import sys
SETTINGS = {
    'server':   'udderweb.com',
    'nick':     'Dot',
    'realname': 'Dot the bot',
    'port':     6667,
    'ssl':      False,
    'channels': ['#test'],
    'executor': {
                'paths': ['scripts']
    }
}

if __name__ == '__main__':
    bot = Bot(SETTINGS)
    bot.connect()
