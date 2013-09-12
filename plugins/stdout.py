from yakr.plugin_base import *
def ready():
   receiveSelfOutput(True)

@match("(.*)")
def output(groups):
    print(groups)
