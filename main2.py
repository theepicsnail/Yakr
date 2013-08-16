import multiprocessing
import Queue
import plugins
import select
from yakr import network

class Plugin():
    def __init__(self, name):
        self.read_pipe = multiprocessing.Queue(100)
        self.write_pipe = multiprocessing.Queue(100)
        self.proc = multiprocessing.Process(
            target = plugins.load_plugin, 
            args = (name, (self.write_pipe, self.read_pipe)))
        self.proc.start()

    def stop(self):
        self.write_pipe.put(None)
        self.write_pipe.close()

    def reader(self):
        return self.read_pipe._reader

    def writer(self):
        return self.read_pipe._reader

    def put(self, line):
        self.write_pipe.put(line)

    def get(self):
        return self.read_pipe.get()

p = Plugin("fortune")
write, read = network.simple_connect(("localhost", 6667))
write.put("NICK Dot")
write.put("USER Dot localhost localhost :foo bar")
while True:
    readable, _, _ = select.select([p.reader(), read._reader],[],[])
    if read._reader in readable: #network has data
        data = read.get()
        if data.startswith("PING"):
            p.put("PONG" + data[4:])
        if data.startswith(":Dot MODE"):
            p.put("JOIN #test")
        if data is None:
            print "End from net"
            break
        print ">", data
        p.put(data)
    if p.reader() in readable: # plugin has data
        data = p.get()
        if data is None:
            print "End from plugin"
            break
        print "<", data
        write.put(data)

p.stop()
