from tests.framework.plugin_test_case import PluginTestCase, main

#def reprocess_line(
class TestRepeater(PluginTestCase):
    def setUp(self):
        self.load_plugin("alias")

    def test_simple_alias(self):
        self.simulate.say("user1", "@test=!repeat test", "#test")
        self.assertEqual(self.outputs, [])
        self.simulate.say("user1", "@test", "#test")
        self.assertNotEqual(self.outputs, [])
        self.assertTrue(self.outputs[0].startswith("::REPROCESS:"))

    def test_alias_with_args(self):
        self.simulate.say("user1", "@test(a,b)=!repeat a b c", "#test")

if __name__ == "__main__":
    main()
