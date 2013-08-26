""" Plugin base
this provides all the functionality needed for a general plugin. 
"""
import re

#Override these functions in your plugin, or dont.
def start():
    pass
def ready():
    pass
def stop():
    pass


def handle_line(line):
    """
    Main message to function converter
    you should probably not over write this function unless you don't need
    the command decorator

    :snail!snail@airc-BD88CA3C PRIVMSG #test :asdf
    """
    process_commands(line)


def process_commands(line):
    match = re.match("^:(.*)!.*PRIVMSG (.*?) :(.*)", line)
    if match:
        sender, dest, msg = match.groups()
        if dest[0] != "#": #Not a channel, assume it's a pm from sender
            dest = sender
        for hook, callback in _commands.items():
            hook_match = re.match(hook, msg)
            if hook_match:
                msg = hook_match.group(1)
                callback(sender, msg, dest)#, hook_match.groups())

#queue stuff
_out_queue = None
def set_out_queue(queue):
    global _out_queue
    _out_queue = queue
def get_out_queue():
    return _out_queue


#irc functions
def _send(line):
    queue = get_out_queue()
    if queue is None:
        return
    queue.put(line)

def join(room):
    _send("JOIN " + room)

def say(to, what):
    _send("PRIVMSG " + to + " :" + what)

def receiveSelfOutput(b):
    _send("::RECEIVE_OUTPUT:" + str(b))

_commands = {}
#command functions
def command(trigger):
    trigger = "^!" + trigger + " (.*)$"
    assert not _commands.has_key(trigger), "Multiple definitions of trigger:" + trigger
    def decorator(func):
        _commands[trigger] = func
        return func
    return decorator

"""
yakr/plugin.py
starts the plugin in another process
loads the module
  module loads plugins/__init__.py
"""

