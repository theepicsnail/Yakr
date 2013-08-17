""" Plugin base
this provides all the functionality needed for a general plugin. 
"""

#Override these functions in your plugin, or dont.
def start():
    pass
def handle_line(line):
    pass
def ready():
    pass
def stop():
    pass

_out_queue = None
def set_out_queue(queue):
    global _out_queue
    _out_queue = queue

def get_out_queue():
    return _out_queue

def join(room):
    get_out_queue().put("JOIN " + room)
def say(to, what):
    get_out_queue().put("PRIVMSG " + to + " :" + what)



"""
yakr/plugin.py
starts the plugin in another process
loads the module
  module loads plugins/__init__.py






"""

