# -*- coding: utf-8 -*-
from . import *

REPLACEMENT_MAP = {
    "<3":u'{C5}♥{}'
}


@match("^:(.*)!.*PRIVMSG (.*?) :(.*)")
def privmsg(groups):
    global REPLACEMENT_MAP
    who, where, what = groups
    original = what
    for find, replace in REPLACEMENT_MAP.items():
        what = what.replace(find, replace)

    if original != what:
        say(where, what)


