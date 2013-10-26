from tests.framework.plugin_test_case import PluginTestCase, main
from random import random

def expect(msg):
    return ["PRIVMSG #test :" + msg]

class TestRepeater(PluginTestCase):
    def setUp(self):
        self.sed = self.load_plugin("sed")

    def test_normal_replace(self):
        self.simulate.say("user1", "foo", "#test")
        self.simulate.say("user1", "!s_foo_bar_", "#test")
        self.assertEqual(self.outputs, expect("bar"))

    def test_ignore_case(self):
        self.simulate.say("user1", "foo 1", "#test") 
        self.simulate.say("user1", "FOO 2", "#test")
        self.simulate.say("user1", "!s_foo_bar_i", "#test")
        self.assertEqual(self.outputs, expect("bar 2"))

    def test_global(self):
        self.simulate.say("user1", "foo", "#test")
        self.simulate.say("user1", "!s_o_e_g", "#test")
        self.assertEqual(self.outputs, expect("fee"))

    def test_colored(self):
        self.simulate.say("user1", "foo", "#test")
        self.simulate.say("user1", "!s_o_o_c", "#test")
        self.assertEqual(self.outputs, expect("f{C4}o{}o"))

    def test_most_recent_match(self):
        self.simulate.say("user1", "foo 1", "#test")
        self.simulate.say("user1", "foo 2", "#test")
        self.simulate.say("user1", "!s_foo __", "#test")
        self.assertEqual(self.outputs, expect("2"))

    def test_chaining(self):
        self.simulate.say("user1", "foo", "#test")
        self.simulate.say("user1", "!s_f_w_ _w_h_", "#test")
        #foo -> woo -> hoo
        self.assertEqual(self.outputs, expect("hoo"))

    def test_cross_room(self):
        self.simulate.say("user1", "foo", "#asdf")
        self.simulate.say("user1", "!s_foo_bar_", "#test")
        self.assertEqual(self.outputs, expect("bar")) 
        #expectes bar in #test even though 'foo' was said in #asdf

    def test_no_match(self):
        self.simulate.say("user1", "!s_asdf_bar_", "#test")
        self.assertEqual(self.outputs, expect(self.sed.NO_MATCH_OUTPUT))

    def test_bad_expression(self):
        self.simulate.say("user1", "!s_foo_bar", "#test")
        self.assertEqual(self.outputs, expect(self.sed.BAD_EXPRESSION_OUTPUT.format("_foo_bar")))

    def test_bad_regex(self):
        self.simulate.say("user1", "!s_+*?_bar_", "#test")
        self.assertEqual(self.outputs, expect(self.sed.BAD_REGEX_OUTPUT.format("+*?")))

if __name__ == "__main__":
    main()
