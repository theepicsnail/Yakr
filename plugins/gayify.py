from yakr.plugin_base import *
from random import randint
@command("gayify")
def gayify(who, what, where):
    out = ""
    for c in what:
        out += "{C%s}" % (randint(2,13)) + c
    say(where, out)
