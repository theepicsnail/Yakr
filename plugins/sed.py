from yakr.plugin_base import *
import re

_SED_COLORS = [4, 7, 3, 10, 6]
_NUM_COLORS = len(_SED_COLORS)
_HISTORY = [''] * 20
_SED_REGEX = (
    "^" #Start of command
    "([^a-zA-Z])" #Delimiter
    "(.*?)" #Search
    "\\1"   #Delimiter
    "(.*?)" #Replace
    "\\1"   #Delimiter
    "(.*?)" #Options
    "(\\1.*|)" # Next sed line
    "$" #End of command
    )

def compile_re(search, flags):
    try:
        if "i" in flags:
            return re.compile(search, re.I)
        return re.compile(search)
    except:
        return None

def find_line(search_re):
    for line in _HISTORY:
        if search_re.search(line):
            return line
    return None

def apply_re(search_re, replacement, flags, line, color_id):

    if "c" in flags:
        replacement = "{C%i}%s{}" % (_SED_COLORS[color_id], replacement)

    count = 1
    if "g" in flags:
        count = 0

    return search_re.sub(replacement, line, count)

@command("s", False)#No space after the command "!s_" is enough to trigger this
def sed(who, what, where):
    extra = what
    working_line = None
    color_id = 0
    while extra:
        match = re.search(_SED_REGEX, extra)
        if not match:
            say(where, "Invalid sed expression: " + extra)
            return
        delim, search, replace, opts, extra = match.groups()

        search_re = compile_re(search, opts)

        if not search_re:
            say(where, "Invalid regex '%s' :(" % search)
            return

        if working_line is None:
            working_line = find_line(search_re)
            if working_line is None:
                say(where, "Couldn't find anything to match that!")
                return

        working_line = apply_re(search_re, replace, opts, working_line, color_id)

        color_id += 1
        if color_id == _NUM_COLORS:
            color_id = 0
    say(where, working_line)

@privmsg
def record(who, what, where):
    global _HISTORY
    if what.startswith("!"):
        return
    _HISTORY.insert(0, what)
    _HISTORY.pop()
