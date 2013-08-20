from SocketServer import TCPServer, StreamRequestHandler, ThreadingMixIn
import threading
"""
Threaded TCP server
http://stackoverflow.com/questions/5218159/start-a-tcpserver-with-threadingmixin-again-in-code-directly-after-shutting-it-d
"""

class Server(TCPServer, ThreadingMixIn):
    class RequstHandler(StreamRequestHandler):
        def handle(self):
            while True:
                msg = self.rfile.readline()
                reply = self.server.process(msg)
                if reply is None:
                    return
                self.wfile.write(reply)

    def __init__(self, host, port, name=None):
        self.allow_reuse_address = True
        TCPServer.__init__(self, (host, port), self.RequstHandler)
        if name is None: name = "%s:%s" % (host, port)
        self.name = name
        self.poll_interval = 1

    def process(self, msg):
        """
        should be overridden
        process a message
        msg    - string containing a received message
        return - if returns a not None object, it will be sent back 
                 to the client.
        """
        raise NotImplemented

    def serve_forever(self, poll_interval=1):
        self.poll_interval = poll_interval
        self.trd = threading.Thread(target=TCPServer.serve_forever,
                                    args = [self, self.poll_interval],
                                    name = "PyServer-" + self.name)
        self.trd.start()

    def shutdown(self):
        TCPServer.shutdown(self)
        TCPServer.server_close(self)
        self.trd.join()
        del self.trd



import Queue
class QueueServer(Server):
    def __init__(self, host, port):
        Server.__init__(self, host, port, "Queue server")
        self.read_queue = Queue.Queue(1)
        self.write_queue = Queue.Queue(1)

    def process(self, data):
        self.read_queue.put(data)
        rep = self.write_queue.get()  
        return rep

