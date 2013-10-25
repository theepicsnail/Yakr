from yakr.plugin_base import *

#To change command prefixes, set it here
#set_command_prefix(...)
#By default the command prefix is '!'

def start():
    #Do any heavy lifting/initialization here
    #irc commands wont work here
    pass

def ready():
    #Any initial irc commands to run go here

    #If you want to be able to handle other plugin's output, uncomment this
    #receiveSelfOutput(True) 

    #commands now available
    join("#somewhere")
    topic("#somewhere", "something")
    say("#somewhere", "something else")
    #think's are reinterpreted like they are lines from the network
    think("PART #somewhere: part message")
    pass

def stop():
    #Close sockets, files, etc...
    pass

#To use a regex to match incoming irc lines
#or if receiveSelfOutput is set, other plugin's output
@match("some (regex)")
def my_handler(capture_groups):
    pass

#To listen to privmsg's (both channel and private) 
@privmsg
def my_privmsg_handler(who, what, where):
    pass

#To listen to a command being executed (e.g. !foo bar baz)
@command("foo")
def my_command_handler(who, what, where):
    #'what' does not have the command or prefix, what="bar baz"
    pass
