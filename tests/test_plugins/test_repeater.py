from tests.framework.plugin_test_case import PluginTestCase, main

class TestRepeater(PluginTestCase):
    def setUp(self):
        self.load_plugin("repeater")

    def nick_chan_msg(self, same_nick, same_channel, same_message, expect_output):
        nick = "snail"
        chan = "#test"
        msg = "hi"

        self.outputs.clear()

        self.simulate.say(nick, msg, chan)
        self.assertEqual(self.outputs, [])

        if not same_nick:
            nick = "lians"
        if not same_message:
            msg = "hello"
        if not same_channel:
            chan = "#test2"

        self.simulate.say(nick, msg, chan)

        if expect_output:
            self.assertEqual(self.outputs, [
                "PRIVMSG {} :{}".format(chan, msg)
            ])
        else:
            self.assertEqual(self.outputs, [])


    def test_repeat_same_nick_same_chan(self):
        for nick in [True, False]:
            for chan in [True, False]:
                for msg in [True, False]:
                    #Right now the repeat plugin will fire across channels
                    self.nick_chan_msg(nick, chan, msg, msg)
if __name__ == "__main__":
    main()
