from tests.framework.plugin_test_case import PluginTestCase, main

n = 0
def linear_chooser(items):
    global n
    out = items[n % len(items)]
    n += 1
    return out

class TestRepeater(PluginTestCase):
    def setUp(self):
        global n
        self.chance_plugin = self.load_plugin("chance")
        self.chance_plugin.chooser = linear_chooser
        n = 0

    def test_magic_8(self):
        #Magic 8 should produce 20 unique outputs
        #Linear choosing should give us the first repeat
        #on the 21st choice
        for _ in xrange(20):
            self.simulate.say("user", "!8", "#test")

        #20 unique outputs
        self.assertEqual(20, len(set(self.outputs)))

        #21st query, should not produce anything new
        self.simulate.say("user", "!8", "#test")
        self.assertEqual(20, len(set(self.outputs)))

    def test_flip(self):
        self.simulate.say("user", "!flip", "#test")
        self.simulate.say("user", "!flip", "#test")
        self.assertEqual(self.outputs, [
            "PRIVMSG #test :user: heads",
            "PRIVMSG #test :user: tails"
        ])

    def test_eastereggs(self):
        expected_output = []
        for key, val in self.chance_plugin._FLIP_EGGS.items():
            self.simulate.say("user", "!flip " + key, "#test")
            expected_output.append("PRIVMSG #test :user: " + val)
if __name__ == "__main__":
    main()
