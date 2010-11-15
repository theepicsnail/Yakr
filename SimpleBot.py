import re
import time

import gevent
from gevent import socket
from gevent import sleep
from gevent import queue

class tcp(object):
    "handles TCP connections"

    def __init__(self, host, port, timeout=300):
        self.ibuffer = ''
        self.obuffer = ''
        self.iqueue = queue.Queue()
        self.oqueue = queue.Queue()
        self.socket = self.create_socket()
        self.host = host
        self.port = port
        self.timeout = timeout

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.socket.connect((self.host, self.port))
        gevent.spawn(self.recv_loop)
        gevent.spawn(self.send_loop)

    def recv_from_socket(self, nbytes):
        return self.socket.recv(nbytes)
    
    def recv_loop(self):
        last_timestamp = time.time()
        while True:
            data = self.recv_from_socket(4096)
            self.ibuffer += data
            while '\r\n' in self.ibuffer:
                line, self.ibuffer = self.ibuffer.split('\r\n', 1)
                self.iqueue.put(line)
                print line

    def send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]
            print ">>> %r" % line
            self.obuffer += line.encode('utf-8', 'replace') + '\r\n'
            while self.obuffer:
                sent = self.socket.send(self.obuffer)
                self.obuffer = self.obuffer[sent:]

irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall

class IRC(object):
    "handles the IRC protocol"

    def __init__(self, server, nick, port=6667, channels=['']):
        self.server = server
        self.nick = nick
        self.port = port
        self.channels = channels
        self.out = queue.Queue() # responses from the server
        self.connect()
        
        # parallel event loop(s), use joinall()
        self.jobs = [gevent.spawn(self.parse_loop),gevent.spawn(self.parse_join)]

    def create_connection(self):
        return tcp(self.server, self.port)

    def connect(self):
        self.conn = self.create_connection()
        gevent.spawn(self.conn.run)
        self.set_nick(self.nick)
        sleep(1)
        self.cmd("USER",
                ['pybot', "3", "*",'Python Bot'])

    def parse_loop(self):
        while True:            
            msg = self.conn.iqueue.get()
            
            if msg == StopIteration:
                self.connect()
                continue
            
            if msg.startswith(":"):  # has a prefix
                prefix, command, params = irc_prefix_rem(msg).groups()
            else:
                prefix, command, params = irc_noprefix_rem(msg).groups()
            nick, user, host = irc_netmask_rem(prefix).groups()
            paramlist = irc_param_ref(params)
            lastparam = ""
            if paramlist:
                if paramlist[-1].startswith(':'):
                    paramlist[-1] = paramlist[-1][1:]
                lastparam = paramlist[-1]
            self.out.put([msg, prefix, command, params, nick, user, host,
                    paramlist, lastparam])
            if command == "PING":
                self.cmd("PONG", paramlist)

    def set_nick(self, nick):
        self.cmd("NICK", [nick])

    def join(self, channel):
        self.cmd("JOIN", [channel])

    def parse_join(self): # this is temporary
        sleep(5)
        for channel in self.channels: [self.join(channel)]

    def cmd(self, command, params=None):
        if params:
            params[-1] = ':' + params[-1]
            self.send(command + ' ' + ' '.join(params))
        else:
            self.send(command)
            
    def send(self, str):
        self.conn.oqueue.put(str)

if __name__ == "__main__":
    bot = IRC('irc.voxinfinitus.net', 'Kaa', 6667, ['#voxinfinitus','#landfill'])
    gevent.joinall(bot.jobs)