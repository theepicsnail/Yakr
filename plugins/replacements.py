# -*- coding: utf-8 -*-
from yakr.plugin_base import *

REPLACEMENT_MAP = {
    "<3":u'{C5}♥{}',
    "LOD":u'ಠ_ಠ',
    "TABLEFLIP":u'(╯°□°）╯︵ ┻━┻)',
    ">:3":"JESUS CHRIST, IT'S A LION! GET IN THE CAR!",
    "i dunno":u"¯\(°_o)/¯",
    "I dunno":u"¯\(°_o)/¯",
    "*shrug*":u"¯\(°_o)/¯",
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
