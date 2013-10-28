import unittest
import sys
import multiprocessing
import yakr.plugin_base

class Simulator(object):
    def __init__(self, callback):
        self.irc_line = callback

    def say(self, who, what, where):
        self.irc_line(u":{}!test@test PRIVMSG {} :{}".format(who, where, what))

#add a put method to a list so that it can act as the message queue
#and be friendly for tests
class PuttableList(list):
    def put(self, item):
        self.append(item)

    def clear(self):
        while len(self) != 0:
            self.pop()
class PluginTestCase(unittest.TestCase):

    def __init__(self, *arg, **kwarg):
        self.outputs = PuttableList()
        self.simulate = Simulator(self.broadcast_to_plugins)
        super(PluginTestCase, self).__init__(*arg, **kwarg)

    def broadcast_to_plugins(self, line):
        if self.loaded_plugin:
            self.loaded_plugin.handle_line(line)

    def load_plugin(self, plugin_name, initialize = True):
        yakr.plugin_base.reset_state()
        plugin_module = __import__("plugins." + plugin_name)
        for sub_module in plugin_name.split("."):
            plugin_module = getattr(plugin_module, sub_module)
        self.loaded_plugin = plugin_module
        if initialize:
            self.initialize_plugin(plugin_module)
        return plugin_module

    def initialize_plugin(self, plugin_module):
        plugin_module.start()
        plugin_module.set_out_queue(self.outputs)
        plugin_module.ready()

    def tearDown(self):
        if self.loaded_plugin:
            self.loaded_plugin.stop()
        super(PluginTestCase, self).tearDown()
        #unload plugin
def main():
     unittest.main()
