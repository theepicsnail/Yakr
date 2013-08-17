"""
This plugin can be imported though importing "pluginTest"
that will import this module, and use __init__ as the plugin module
"""
from .. import * #pull in the plugin stuff from the parent package

def ready():
    join("#test")
    say("#test", "foo")
