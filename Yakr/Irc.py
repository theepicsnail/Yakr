import gevent
from gevent import socket, queue
from Logger import logger
from Networking import *
from Plugin import *
from os import walk
from Bot import *
from Executor import *

class IrcNullMessage(Exception):
    pass


class Bot(BotBase):
    '''Provides a basic interface to an IRC server.'''
    
    def __init__(self, settings):
        self.server = settings['server']
        self.nickname = settings['nick']
        self.realname = settings['realname']
        self.port = settings['port']
        self.ssl = settings['ssl']
        self.channels = settings['channels']
        self.line = {'prefix': '', 'command': '', 'args': ['', '']}
        self.lines = queue.Queue() # reesponses from the server
        self.commands = queue.Queue() 
        self.logger = logger
        self.executor = Executor(settings.get('executor',{}))
        self.context = ['']*20 #how many messages to keep
        self.commandLeader = ">"


    # BotBase functions {{{
    def connect(self):
        self._connect() 
        gevent.spawn(self._command_processor)
        self._event_loop()
         
    def quit(self):
        logger.info("Quitting.")
        self.conn.disconnect()

    def nick(self, newNick=None):
        if newNick:
            self.cmd('NICK', newNick)
            self.nickname = newNick
        else:
            return self.nickname

    def msg(self, target, msg):
        self.cmd('PRIVMSG', (target + ' :' + msg))
    def join(self,channel):
        self.cmd('JOIN',channel)
    def part(self,channel):
        self.cmd('PART',channel)
    # }}}

    def _create_connection(self):
        transport = SslTcp if self.ssl else Tcp
        return transport(self.server, self.port)
    
    def _connect(self):
        self.conn = self._create_connection()
        gevent.spawn(self.conn.connect)
        self.nick(self.nickname)
        self.cmd('USER', (self.nickname, ' 3 ', '* ', self.realname))
    
    
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
                    self.nick(self.nick)
                    continue
                if command == 'PING':
                    self.cmd('PONG', args)
                    continue
                if command == '001':
                    self._join_chans(self.channels)
                    continue
                if command == 'PRIVMSG':
                    if args[1].startswith(self.commandLeader):
                        cmd = args[1].replace(self.commandLeader,"",1)
                        target = args[0]
                        if target == self.nickname:
                            target = prefix.split('!')[0]
                        self.commands.put((target,cmd))
                    
        except:
            self.quit()
    
    def _command_processor(self):
        '''
        Pull commands from the command queue and run them.
        '''
        running = True
        while running:
            try:
                target,command = self.commands.get()
                resp = self.executor.execute(command)
                self.msg(target,resp)
            except gevent.GreenletExit:
                running = False
            except Exception as exc:
                import traceback
                traceback.print_exc()

        return


    def _join_chans(self, channels):
        return [self.cmd('JOIN', channel) for channel in channels]
    
    
    def cmd(self, command, args, prefix=None):
        
        if prefix:
            self._send(prefix + command + ' ' + ''.join(args))
        else:
            self._send(command + ' ' + ''.join(args))
            
    def _send(self, s):
        logger.info(s)
        self.conn.oqueue.put(s)


