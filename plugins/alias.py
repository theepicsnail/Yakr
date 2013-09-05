from . import *
import re
import pickle

set_command_prefix("@")
_ALIASES = {}
ALIAS_STORE = "Aliases.pkl"

def start():
    global _ALIASES
    try:
        _ALIASES = pickle.load(file(ALIAS_STORE))
    except:
        _ALIASES = {}
def stop():
    pickle.dump(_ALIASES, file(ALIAS_STORE,"w"))


#!alias foo=!w 95134
#!alias bar(baz)=@baz
#then
#@bar(foo) -> 2nd rule -> @foo -> reprocessing -> first rule -> !w 95134 

#@true(p,q)=p
#@false(p,q)=p
#@and(p,q)=@p(q,p)
#@and(false,true) -> @true(false,true) -> false

_ALIAS_RE = re.compile(
    "^"             #START
    "([a-zA-Z]+)"      #required name (a-z)
    "(\([a-zA-Z,]+\)|)"#optional arguments "(a,b,c)"
    "(=.+|)"        #optional assignment "=some command"
    "(.*?)"         #overflow, only invalid lines put data here
    "$")            #END

@command("")
def fire_alias(who, what, where):
    #possible 'what's
    #foo
    #foo(a,b)
    #foo=...
    #foo(a,b)=...
    
    match = _ALIAS_RE.match(what)
    if not match:
        return

    name, args, assignment, errors = match.groups()
    #('foo', '', '', '')
    #('foo', '(a,b)', '', '')
    #('foo', '', '=...', '')
    #('foo', '(a,b)', '=...', '')
    #last group gets a value when parsing failed
    #"foo(a" => ('foo', ''. ''. '(a')
    if errors:
        say(where, "Error parsing {}{{C3}}{}".format(name, errors))
        return

    if args:
        args = args[1:-1].split(",")
    else:
        args = []

    if assignment:
        assignment = assignment[1:]
    else:
        assignment = None

    if assignment is not None:
        assigned = _ALIASES.get(who, {})
        assigned[name] = (args, assignment)
        _ALIASES[who] = assigned
    else:
        replacement = _ALIASES.get(who, {}).get(name, False)
        if replacement:
            rep_args, rep_str = replacement
            if len(args) != len(rep_args):
                say(where, "Argument mismatch. Provided:{}, Expected:{}."
                    .format(len(args), len(rep_args)))
                return
            #Super awesome replace code. 
            replacement_map = dict(zip(rep_args, args))
            parts = re.split("(%s)" % "|".join(rep_args), rep_str)
            parts[1::2] = [replacement_map[key] for key in parts[1::2]]
            rep_str = "".join(parts)

            print what, "=>", rep_str
            think(":{}! PRIVMSG {} :{}".format(
                who,
                where,
                rep_str))

