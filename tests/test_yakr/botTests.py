import tests.plugin
from yakr import plugin
#Drop the testing plugin class over the yakr.plugin.Plugin class.
plugin.Plugin = tests.plugin.TestingPlugin

from yakr.bot import Bot
import unittest
from Queue import Empty
from multiprocessing import Queue
from threading import Thread
#Overwrite the Plugin class with one usable for testing


def skip_handshake(test_method):
    def new_method(self):
        self.net_read.get(True, .01)
        self.net_read.get(True, .01)
        test_method(self)
    return new_method

class TestYakrBot(unittest.TestCase):
    def setUp(self):
        #Net queues are the queues going into the bot
        #from the "network"
        #net_write is what you write to when simulating
        #data going into the bot.
        #net_read is what the bot outputs to
        self.net_write = Queue(10)
        self.net_read = Queue(10)
        self.bot = Bot((self.net_read, self.net_write))
        self.bot_process = Thread(target =self.bot.run)
        self.bot_process.start()

    def tearDown(self):
        if self.bot_process.is_alive():
            self.net_write.put(None)
            self.bot_process.join()

    def test_handshake(self):
        nick_line = self.net_read.get(True, .01)  
        assert nick_line.startswith("NICK")

        user_line = self.net_read.get(True, .01)  
        assert user_line.startswith("USER")

        try:
            data = self.net_read.get(True, .01)
            assert False, "Expected no data, got:" + repr(data)
        except Empty:
            pass

    @skip_handshake
    def test_pingpong(self):
        self.net_write.put("PING 1234")
        
        response = self.net_read.get(True, .01)
        assert response == "PONG 1234", "Espected 'PONG 1234', got:" + repr(response)
   
    def test_loading(self):
        self.bot.load("TestPlugin")
        assert "TestPlugin" in self.bot.plugin_map
        self.bot.unload("TestPlugin")
        assert "TestPlugin" not in self.bot.plugin_map
        self.bot.cycle("TestPlugin")
        assert "TestPlugin" in self.bot.plugin_map

    @skip_handshake
    def test_ready(self):
        self.bot.load("Plugin1")
        plugin1 = self.bot.plugin_map["Plugin1"]
        self.net_write.put(":server.com 001 Dot :"
            + "Welcome to the TestIrc Network Dot!Dot@localhost")
        msg = plugin1.write_queue.get()
        assert msg == "::STATE:READY", "expected ::STATE:READY, got: "+msg
        plugin1.write_queue.get()

        self.bot.load("Plugin2")
        msg = self.bot.plugin_map["Plugin2"].write_queue.get()
        assert msg == "::STATE:READY", "expected ::STATE:READY, got: "+msg
if __name__ == "__main__":
    unittest.main()
