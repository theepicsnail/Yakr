from tests.framework.plugin_test_case import PluginTestCase, main
from time import sleep
from random import random
def random_message():
    return str(random())

class TestRepeater(PluginTestCase):
    def setUp(self):
        self.load_plugin("ping")

    def test_does_not_ping_empty_message(self):
        self.simulate.say("user1", "!ping", "#test")
        sleep(1)
        self.assertEqual(self.outputs, [])

    def test_does_ping_localhost(self):
        self.simulate.say("user1", "!ping localhost", "#test")
        sleep(5)
        self.assertEqual(len(self.outputs), 3)
        self.assertEqual(self.outputs[0], "PRIVMSG #test :pinging localhost")
        self.assertTrue("resolved to" in self.outputs[1]) #could be 'localhost' could be '::1'
        self.assertTrue(self.outputs[2].endswith("{} ms")) #got back some value

if __name__ == "__main__":
    main()
