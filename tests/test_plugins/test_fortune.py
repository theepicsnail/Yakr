# -*- coding: utf-8 -*-
from tests.framework.plugin_test_case import PluginTestCase, main
import time

def fortune_initialized(test):
    def func(self):
        self.initialize_plugin(self.fortune)
        return test(self)
    return func

class FakeFortune:
    def __init__(self, fortune_module):
        self.fortune = fortune_module
        self.old_get_fortune = fortune_module.get_fortune
        fortune_module.get_fortune = self.get_next_fortune

    def get_next_fortune(self):
        return self.next_fortune

    def set_fortune(self, fortune):
        self.next_fortune = fortune

    def __exit__(self, type, value, traceback):
        self.fortune = self.old_get_fortune

    def __enter__(self):
        return self

class TestRepeater(PluginTestCase):
    def setUp(self):
        #Unitialized. self.initialize_plugin(self.fortune) needs called.
        self.fortune = self.load_plugin("fortune", False)
        #Set fortunes to fire asap
        self.fortune._MIN_WAIT = .1
        self.fortune._MAX_WAIT = .1
        self.initialize_plugin(self.fortune)


    def test_unicode_fortune(self):
        with FakeFortune(self.fortune) as fortune_faker:
            unicode_line = u"♥"
            fortune_faker.set_fortune(unicode_line)
             
            self.simulate.say("user", "!fortune", "#test")
            self.assertEqual(self.outputs, ["PRIVMSG #test :" + self.fortune.FORTUNE_TEMPLATE % unicode_line])

    def test_action_trigger(self):
        with FakeFortune(self.fortune) as fortune_faker:
            fortune_faker.set_fortune("test")
            self.simulate.say("user", "message", "#test")
            time.sleep(.1)
            self.assertEqual(self.outputs, ["PRIVMSG #test :" + self.fortune.RANDOM_FORTUNE_TEMPLATE % "test"])
    

if __name__ == "__main__":
    main()
