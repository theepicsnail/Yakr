from tests.plugin_test_environment import PluginTestCase, main

class TestRepeater(PluginTestCase):
    def setUp(self):
        self.load_plugin("tell")

    def test_tell(self):
        self.simulate.say("teller", "!tell told i told you so", "#test")
        self.assertEqual(self.outputs, [
        u"PRIVMSG #test :teller: I'll make sure to tell told next time I see them!"
        ])
        self.outputs.clear()

        self.simulate.say("told", "what?", "#test")
        self.assertEqual(len(self.outputs), 2)

if __name__ == "__main__":
    main()
