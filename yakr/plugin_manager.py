"""
plugin manager stores a map of all the loaded plugins and does some of the
queue management.
"""
from plugin import Plugin

class PluginManager(object):

    def __init__(self):
        self.plugin_map = {}

    def load(self, plugin_name):
        """ Load a plugin """
        if self.plugin_map.has_key(plugin_name):
            print plugin_name, "already loaded"
            return
        plugin = Plugin(plugin_name)
        self.plugin_map[plugin_name] = plugin

    def unload(self, plugin_name):
        """ Unload a plugin """
        if not self.plugin_map.has_key(plugin_name):
            print plugin_name, "not loaded"
            return
        self.plugin_map[plugin_name].stop()
        del self.plugin_map[plugin_name]

    def cycle(self, plugin_name):
        """ Load a plugin, unloading first it if it exists. """
        self.unload(plugin_name)
        self.load(plugin_name)

         
