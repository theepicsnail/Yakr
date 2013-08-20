"""
Tests for yakr.network
"""
from yakr import network 
import unittest
from tests.server import QueueServer
from threading import Timer
from time import time

class TestYakrNetwork(unittest.TestCase):
    """ Test case for yakr.network """

    def setUp(self):
        self.server = QueueServer("localhost", 0)
        self.server.serve_forever()
        self.hostport = self.server.socket.getsockname()
        self.net_write, self.net_read = network.simple_connect(self.hostport)
        self.server_read = self.server.read_queue
        self.server_write = self.server.write_queue

    def tearDown(self):
        self.net_write.put(None)
        self.server_write.put(None)
        self.server.shutdown()


    def test_simple_connect(self):
        for _ in xrange(3):
            #test net_write data is received on the server properly
            #Sending "Hello" through yakr.network will append the \r\n
            self.net_write.put("Hello")
            msg = self.server_read.get() #fetch data from server side
            assert msg == "Hello\r\n", "Expected 'Hello', got: " + repr(msg)

            #test server data comes out of net_read properly
            self.server_write.put("World\r\n")
            msg = self.net_read.get()
            assert msg == "World", "Expected 'World', got: " + repr(msg)

    def test_message_delimiter(self):
        # blank message for server to reply to
        # in the testing server, client must send first message
        self.net_write.put("") 
        self.server_read.get()
        self.server_write.put("message1\r\nmessage2\r\n")
        assert self.net_read.get() == "message1"
        assert self.net_read.get() == "message2"

        self.net_write.put("")
        self.server_read.get()
        no_delimiters = "message3\nmessage4\rmessage5\n\rmessage6"
        self.server_write.put(no_delimiters+"\r\n")
        assert self.net_read.get() == no_delimiters

    def test_buffer_until_delimiter(self):
        self.net_write.put("")
        self.server_read.get()
        self.server_write.put("partial me")
        
        def finish_message():
            self.net_write.put("")
            self.server_read.get()
            self.server_write.put("ssage\r\n")

        start_receiving_time = time()
        Timer(.5, finish_message).start()
        msg = self.net_read.get()
        end_receiving_time = time()
    
        assert msg == "partial message"
        assert end_receiving_time - start_receiving_time > .5 #at LEAST .5 seconds, (timer + construction + network delay). 
        #if it's shorter than .5, then we know that the timer didn't prevent the message from unblocking

if __name__ == '__main__':
    unittest.main()
