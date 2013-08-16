""" Plugin base
"""
import signal
import sys

DEFAULT_PREFIX = "!"
_DATA_OUT = None

def signal_handler(signal, frame):
    print "Plugin interrupted. Shutting down."
    if _DATA_OUT is not None:
        _DATA_OUT.put(None)
    sys.exit(0)

def load_plugin(plugin_name, (data_in, data_out)):
    """Main entry point of plugins.
    plugin_name - the plugin to load
    data_in - read only multiprocessing connection
    data_out - write only multiprocessing connection
    """
    plugin_module = getattr(__import__("plugins."+plugin_name), plugin_name)
    global _DATA_OUT
    _DATA_OUT = data_out

    signal.signal(signal.SIGINT, signal_handler)
    
    command = plugin_module.__dict__.get("COMMAND", None)
    if command == True:
        command = plugin_module.__name__.split(".",1)[1]

    prefix = plugin_module.__dict__.get("PREFIX", DEFAULT_PREFIX)
    print "command", command
    print "prefix", prefix

    while True:
        data = data_in.get()
        if data is None:
            print "caught exit signal"
            return

        data_out.put(data)
        print ">", data



def msg(who, what):
    """ send a message to a channel or nick """
    _DATA_OUT.send("PRIVMSG %s :%s" % (who, what))
