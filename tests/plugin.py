from multiprocessing import Queue

class TestingPlugin():
    def __init__(self, plugin_name):
        self.read_queue = Queue(10)
        self.write_queue = Queue(10)
        #unlike real plugins, don't launch a new process
    def reader(self):
        return self.read_queue._reader
    def writer(self):
        return self.write_queue._writer
    def stop(self):
        pass
    def put(self, value):
        self.write_queue.put(value)
    def get(self):
        return self.read_queue.get()
