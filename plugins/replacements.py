# -*- coding: utf-8 -*-
from . import *

REPLACEMENT_MAP = {
    "<3":u'{C5}♥{}',
    "LOD":u'ಠ_ಠ'
}


@match("^:(.*)!.*PRIVMSG (.*?) :(.*)")
def privmsg(groups):
    global REPLACEMENT_MAP
    who, where, what = groups
    original = what
    for find, replace in REPLACEMENT_MAP.items():
        what = what.replace(find, replace)

    if "\o/" in original:
        spaces = [
            " "*len(segment)
            for segment in original.split("\o/")
        ]
        say(where, "YAY".join(spaces))
        say(where, "/ \\".join(spaces))
    elif original != what:
        say(where, what)
