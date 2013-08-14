import os, sys

SUCCESS, FAIL, EXISTS, NOTEXISTS = "SUCCESS", "FAIL", "EXISTS", "NOT EXISTS"

class PluginManager(object):
    def __init__(self):
        self.plugin_map = {}

    def load(self, plugin_name):
        if self.plugin_map.has_key(plugin_name):
            return EXISTS
        try:
            plugin = __import__("plugins." + plugin_name + "." + plugin_name)
        except ImportError:
            return FAIL

        self.plugin_map[plugin_name] = plugin
        return SUCCESS

    def unload(self, plugin_name):
        if not self.plugin_map.has_key(plugin_name):
            return NOTEXISTS
        module = self.plugin_map[plugin_name]

        # sys.getrefcount(module) => 4 here
        # 1) module in plugin_map
        # 2) module in sys.modules
        # 3) module reference we just delcared
        # 4) temporary reference used in getrefcount

        del self.plugin_map[plugin_name]
        del sys.modules[module.__name__]
        del module

        return SUCCESS

    def cycle(self, plugin_name):
        self.unload(plugin_name)
        self.load(plugin_name)

def discover_plugins(base_dir):
    """Given the plugin path, search it for loadable plugins.
    A plugin is considered loadable if both
        base_dir/<plugin>/__init__.py
    and
        base_dir/<plugin>/<plugin>.py
    exist
    """
    return [
        plugin
        for plugin in os.listdir(base_dir)
        if os.path.exists(os.path.join(base_dir, plugin, "__init__.py"))\
        and os.path.exists(os.path.join(base_dir, plugin, "__init__.py"))
    ]

if __name__ == "__main__":
    p = PluginManager()
    p.load("plugins")
    p.unload("ConfigParser")
