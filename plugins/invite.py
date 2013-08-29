from . import *

@match(".*INVITE.*:(.*)")
def on_invite(groups):
    join(groups[0])
