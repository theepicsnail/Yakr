import gevent
from gevent import socket, queue
from Logger import logger
from os import walk
from Networking import *

class RealBot:
    '''Provides a basic interface to an IRC server.'''

    def __init__(self, settings):
        self.server = settings['server']
        self.nickname = settings['nick']
        self.realname = settings['realname']
        self.port = settings['port']
        self.ssl = settings['ssl']
        self.line = {'prefix': '', 'command': '', 'args': ['', '']}
        self.lines = queue.Queue()  # responses from the server
        self.commands = queue.Queue()
        self.logger = logger
        self.conn = None
        self.eventLoop = None

    def start(self):
        transport = SslTcp if self.ssl else Tcp
        self.conn = transport(self.server, self.port)
        gevent.spawn(self.conn.connect)

        self.cmd('NICK', self.nickname)
        self.cmd('USER', (self.nickname, ' 3 ', '* ', self.realname))
        gevent.spawn(self._command_processor)
        self.eventLoop = gevent.spawn(self._event_loop)

    def wait(self):
      self.eventLoop.join()

    def onReady(self):
      pass

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
                logger.info("> " + line)
                prefix, command, args = self._parsemsg(line)
                self.line = {'prefix': prefix,
                             'command': command,
                             'args': args}
                self.lines.put(self.line)
                if command == '433':  # nick in use
                    self.onNickCollision()
                    self.nick = self.nick + '_'
                    self.nick(self.nick)
                    continue
                if command == 'PING':
                    self.cmd('PONG', args)
                    continue
                if command == '001':
                    self.onReady(self)
                    continue

#                self.commands.put((target, cmd))

        except Exception as e:
            logger.exception(e)
            self.quit()

    def _command_processor(self):
        '''
        Pull commands from the command queue and run them.
        '''
        running = True
        while running:
            try:
                target, command = self.commands.get()
                resp = self.executor.execute(command)
                self.msg(target, resp)
            except gevent.GreenletExit:
                logger.info("command processor caught greenlet exit.")
                running = False
            except Exception as exc:
                logger.info("command processor caught exception.", exc)
                import traceback
                traceback.print_exc()
        logger.info("command processor exited.")
        
        return

    def cmd(self, command, args, prefix=""):
        s = prefix + command + ' ' + ''.join(args)
        logger.info("< " + s)
        self.conn.oqueue.put(s)
