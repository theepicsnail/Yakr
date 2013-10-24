""" Plugin base
this provides all the functionality needed for a general plugin. 
"""
import re

_out_queue = None
_command_prefix = None
_commands = {}
_matches = {}
def reset_state():
    global _out_queue, _command_prefix, _commands, _matches
    _command_prefix = "!"
reset_state()

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

    #print "--handle line--"
    #print "line:", line
    #print "Commands:", _commands

    process_commands(line)
    process_matches(line)

def process_commands(line):
    match = re.match("^:(.*)!.*PRIVMSG (.*?) :(.*)", line)
    if match:
        sender, dest, msg = match.groups()
        if dest[0] != "#": #Not a channel, assume it's a pm from sender
            dest = sender
        for hook, callback in _commands.items():
            hook_match = re.match(hook, msg)
            if hook_match:
                m = hook_match.group(1).strip()
                callback(str(sender), m, dest)#, hook_match.groups())
def process_matches(line):
    for match_re, func in _matches.items():
        results = re.match(match_re, line)
        if results:
            func(results.groups())
#queue stuff
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
    if type(what) == str:
        what = what.decode("utf-8")
    _send(u"PRIVMSG {} :{}".format(to, what))

def topic(room, text):
    _send("TOPIC " + room +" :" + text.decode('utf-8'))

def receiveSelfOutput(b):
    _send("::RECEIVE_OUTPUT:" + str(b))

def think(irc_line):
    _send("::REPROCESS:" + irc_line)

#command functions
def command(trigger, requireSpace = True):
    trigger = "^" + _command_prefix + trigger
    if requireSpace :
        trigger += " "
    trigger += "(.*)$"
    assert not _commands.has_key(trigger), "Multiple definitions of trigger:" + trigger
    def decorator(func):
        _commands[trigger] = func
        return func
    return decorator
def set_command_prefix(prefix):
    global _command_prefix
    _command_prefix = prefix

def match(trigger):
    def decorator(func):
        _matches[trigger] = func
        return func
    return decorator

def privmsg(func):
    _commands["(.*)"]=func


"""
yakr/plugin.py
starts the plugin in another process
loads the module
  module loads plugins/__init__.py
"""
