from tests.framework.plugin_test_case import PluginTestCase, main
from random import random

#Use a random message so that the chance of a previous success leaking
#into a newly failing test and hiding it is nil.
def random_message():
    return str(random())

def get_reprocess_line(who, what, where):
    return '::REPROCESS::{}! PRIVMSG {} :{}'.format(who, where, what) 

class TestRepeater(PluginTestCase):
    def setUp(self):
        self.alias_plugin = self.load_plugin("alias")
        #Clear aliases to get a fresh dict
        self.alias_plugin._ALIASES={}

    def test_arg_parser(self):
        def test_parse(arg_str, expectation):
            result = self.alias_plugin.parse_call("(" + arg_str +")")
            if expectation == False:
                self.assertFalse(result)
            else:
                self.assertEqual(expectation, result['args'])
        test_parse("", [""])
        test_parse("x", ["x"])
        test_parse("x,y", ["x", "y"])
        test_parse("g(x)", ["g(x)"])
        test_parse("f(g(x))", ["f(g(x))"])
        test_parse("f(g(x,y))", ["f(g(x,y))"])
        test_parse("f(g(x,y)),z", ["f(g(x,y))","z"])
        test_parse(",", ["", ""])
        


    def test_new_nick_saves(self):
        self.assertFalse("user1" in self.alias_plugin._ALIASES)
        self.simulate.say("user1", "@test=123", "#test")
        self.assertTrue("user1" in self.alias_plugin._ALIASES)

    def test_simple_alias(self):
        msg = random_message()
        self.simulate.say("user1", "@test="+msg, "#test")
        self.assertEqual(self.outputs, [])
        self.simulate.say("user1", "@test", "#test")
        self.assertNotEqual(self.outputs, [])
        self.assertEqual(self.outputs, 
            [get_reprocess_line("user1", msg, "#test")])

    def test_alias_with_args(self):
        msg = random_message()
        self.simulate.say("user1", "@test(a,b)=a b " + msg, "#test")
        self.simulate.say("user1", "@test(1,2)", "#test")
        self.assertEqual(self.outputs,
            [get_reprocess_line("user1", "1 2 " + msg, "#test")])

    def test_composition(self):
        msg = random_message()
        self.simulate.say("user1", "@test(a)=a", "#test")
        self.simulate.say("user1", "@test2(a,b)=a " + msg, "#test")

        self.simulate.say("user1", "@test(@test2(X, Y))", "#test")
        self.assertEqual(self.outputs, [get_reprocess_line("user1", "@test2(X, Y)", "#test")])
        self.outputs.clear()

        #do the reprocessing 
        self.simulate.say("user1", "@test2(X, Y)", "#test")
        self.assertEqual(self.outputs, [get_reprocess_line("user1", "X " + msg, "#test")])

    def test_formatting(self):
        msg = random_message()
        msg2= random_message()
        self.simulate.say("user1", "@test = " + msg, "#test")
        self.simulate.say("user1", "@TEST2 ( foo1, BAR ) = foo1 BAR " + msg2, "#test")
        self.assertEqual(self.outputs, [])

        self.simulate.say("user1", "@test", "#test")
        self.assertEqual(self.outputs, 
            [get_reprocess_line("user1", msg, "#test")])
        self.outputs.clear()
        
        self.simulate.say("user1", "@TEST2  ( 123 , 45 67  )", "#test")
        self.assertEqual(self.outputs,
            [get_reprocess_line("user1", "123 45 67 " + msg2, "#test")])

    def test_not_channel_specific(self):
        msg = random_message()
        self.simulate.say("user1", "@test=" + msg, "#test")
        self.simulate.say("user1", "@test", "#otherRoom")
        self.assertEqual(self.outputs, 
            [get_reprocess_line("user1", msg, "#otherRoom")])

    def test_is_nick_specific(self):
        msg = random_message()
        self.simulate.say("user1", "@test="+msg, "#test")
        self.simulate.say("user2", "@test", "#otherRoom")
        self.assertEqual(self.outputs, [])

if __name__ == "__main__":
    main()
