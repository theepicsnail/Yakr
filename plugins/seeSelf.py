from yakr.plugin_base import *

def ready():
    receiveSelfOutput(True)
    
def handle_line(line):
    print "seeSelf line:", line
