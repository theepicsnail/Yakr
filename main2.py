import multiprocessing
import Queue
import plugins
#from bot import networking

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
import time
end = time.time() + 60
while time.time() < end:
    p.put("hello")
    v = p.get()
    if v is None:
        print "Process interrupted"
        break
    print v
p.stop()
time.sleep(10)
