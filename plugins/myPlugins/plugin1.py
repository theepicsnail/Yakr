
#Because __init__ does from .. import *, we can just pull the plugin stuff from there into here
from . import *

def ready():
    say("#test", "plugin1")
