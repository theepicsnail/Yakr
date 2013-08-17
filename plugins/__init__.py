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

def _send(line):
    queue = get_out_queue()
    if queue is None:
        return
    queue.put(line)

def join(room):
    _send("JOIN " + room)

def say(to, what):
    _send("PRIVMSG " + to + " :" + what)



"""
yakr/plugin.py
starts the plugin in another process
loads the module
  module loads plugins/__init__.py






"""

