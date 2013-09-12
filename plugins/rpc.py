from yakr.plugin_base import *
def ready():
    receiveSelfOutput(True)

set_command_prefix("$")

@command("")
def shell(who, what, where):
    
    #('snail', '$!w 95134 | !s_.*feels like ([^ ]+).*_\1_', '#adullam')
    #this breaks into
    #('snail', '!w 95134', '#adullam')
    #('snail', '!s .....', '#adullam')

    #then we link it as an rpc chain
    #('snail', '!w 95134', 'RPC1')
    #('snail', '!s .....', 'RPC2')

    #Attach listeners for RPC1 and RPC2
    #When !w outputs into RPC1
    #  Take the output "San Jose..."
    #  Think ":snail!... PRIVMSG RPC2 :San jose..."
    #  Fire !s
    
    #When !s outputs into RPC2
    #  Take the output "57.3"
    #  Since there's no next RPC
    #  we output it to #adullam

    
    
