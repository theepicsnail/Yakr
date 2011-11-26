import gevent
from gevent import socket, queue
from Logger import logger
from Networking import *
from Plugin import *
from os import walk
import Action
class IrcNullMessage(Exception):
    pass


class Bot(object):
    '''Provides a basic interface to an IRC server.'''
    
    def __init__(self, settings):
        self.server = settings['server']
        self.nick = settings['nick']
        self.realname = settings['realname']
        self.port = settings['port']
        self.ssl = settings['ssl']
        self.channels = settings['channels']
        self.line = {'prefix': '', 'command': '', 'args': ['', '']}
        self.lines = queue.Queue() # responses from the server
        self.logger = logger
        self.plugins = PluginManager(settings['pluginPath'])
        Action.bot = self
    def start(self):
        gevent.spawn(self._start_plugins)
        self._connect() 
        self._event_loop()
        
    def _start_plugins(self):
        self.plugins.autoload()
        while True:
            line = self.lines.get()
            logger.debug("Plugin handle line: <{}>".format(len(self.plugins.plugins())))
            for name,mod in self.plugins.plugins():
                logger.debug("<{}> handle_line".format(name))
                try:
                    mod.handle_line(line)
                except:
                    logger.exception("Plugin threw an exception!\n{}\n{}".format(name,line))
        #load plugins
        #pull something from self.lines
            #Give that to each of the plugins
    def _stop_plugins(self):
        logger.info("Unloading plugins")
        for name,mod in self.plugins.plugins():
            self.plugins.unload(name)

    def _shutdown(self):
        logger.info("Shutting down.")
        self._disconnect()
        self._stop_plugins()

    def _create_connection(self):
        transport = SslTcp if self.ssl else Tcp
        return transport(self.server, self.port)
    
    def _connect(self):
        self.conn = self._create_connection()
        gevent.spawn(self.conn.connect)
        self._set_nick(self.nick)
        self.cmd('USER', (self.nick, ' 3 ', '* ', self.realname))
    
    def _disconnect(self):
        self.conn.disconnect()
    
    def _parsemsg(self, s):
        '''
        Breaks a message from an IRC server into its prefix, command, 
        and arguments.
        '''
        
        prefix = ''
        trailing = []
        if not s:
            raise IrcNullMessage('Received an empty line from the server.')
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args
    
    def _event_loop(self):
        '''
        The main event loop.
        
        Data from the server is parsed here using `parsemsg`. Parsed events
        are put in the object's event queue, `self.events`.
        '''
        try:
            while True:
                line = self.conn.iqueue.get()
                logger.info(line)
                prefix, command, args = self._parsemsg(line)
                self.line = {'prefix': prefix, 'command': command, 'args': args}
                self.lines.put(self.line)
                if command == '433': # nick in use
                    self.nick = self.nick + '_'
                    self._set_nick(self.nick)
                if command == 'PING':
                    self.cmd('PONG', args)
                if command == '001':
                    self._join_chans(self.channels)
        except:
            self._shutdown()
    def _set_nick(self, nick):
        self.cmd('NICK', nick)
    
    def _join_chans(self, channels):
        return [self.cmd('JOIN', channel) for channel in channels]
    
    def reply(self, prefix, msg):
        self.msg(prefix.split('!')[0], msg)
    
    def msg(self, target, msg):
        self.cmd('PRIVMSG', (target + ' :' + msg))
    
    def cmd(self, command, args, prefix=None):
        
        if prefix:
            self._send(prefix + command + ' ' + ''.join(args))
        else:
            self._send(command + ' ' + ''.join(args))
            
    def _send(self, s):
        logger.info(s)
        self.conn.oqueue.put(s)


