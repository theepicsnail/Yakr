""" 
yakr utilities
right now it's just process naming stuff
"""
from ctypes import cdll, byref, create_string_buffer
def set_procname(newname):
    """
    Sets the current process's name (as displayed in pstree)
    http://blog.abhijeetr.com/2010/10/changing-process-name-of-python-script.html
    """
    libc = cdll.LoadLibrary('libc.so.6')    
    buff = create_string_buffer(len(newname) + 1)
    buff.value = newname.encode("ascii")
    libc.prctl(15, byref(buff), 0, 0, 0)


import multiprocessing
def named_runner(run):
    """
    when launching a new process in multiprocessing, you can specify a name
    for the process. That name is basically useless. However, if you wrap
    your target in named_runner, the name in that process, will be set to
    the name that shows up in pstree

    multiprocessing.Process(
        target = named_runner(original_target),
        name = "Process Name",
        args = (...),
        kwargs = {...})
    will launch original_target as expected, and the process created will
    show us as "Process Name" in system tools
    """

    def runner(*argv, **kwargs):
        """
        the returned function, that actually gets called when the process
        starts.
        Essentually this just makes the first line of the new process a 
        call to set_procname
        """

        set_procname(multiprocessing.current_process().name)
        return run(*argv, **kwargs)
    return runner

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
#http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):
    import htmlentitydefs, re
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

_03 = chr(3)
_COLOR_MAP = {}

_VALS = [str(n) for n in range(16)]
#Build mappings
for fg in _VALS:
    for bg in _VALS:
        _COLOR_MAP["C{},{}".format(fg, bg)] =\
            _03 + fg +"," + bg.zfill(2)
for v in _VALS:
    code = _03 + v.zfill(2)
    _COLOR_MAP["C{}".format(v)] = code
    _COLOR_MAP["C{},".format(v)] = code

    code = _03 + "," + v.zfill(2)
    _COLOR_MAP["C,{}".format(v)] = code


_COLOR_MAP["C"] = chr(15)  #{C} = reset colors
_COLOR_MAP[""] = chr(15)   #{} = reset colors
_COLOR_MAP["B"] = chr(0x02)#{B} bold
_COLOR_MAP["U"] = chr(0x1F)#{U} underline
_COLOR_MAP["R"] = chr(0x12)#{R} reverse
_COLOR_MAP["LINK"] = "\x1F\x032\02\02"
def parse_colors(line):
    for code, replacement in _COLOR_MAP.items():
        line = line.replace("{{{}}}".format(code), replacement)
    return line
