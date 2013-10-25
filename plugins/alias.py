from yakr.plugin_base import *
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
    "(\w+)"         #required name (a-z)
    "\s*"
    "(\([\w,]+\)|)" #optional arguments "(a,b,c)"
    "(=.+|)"        #optional assignment "=some command"
    "(.*?)"         #overflow, only invalid lines put data here
    "$")            #END

@command("", False)
def fire_alias(who, what, where):
    assignment = parse_assignment(what)
    if assignment:
        handle_assignment(who, assignment)
        return

    call = parse_call(what)
    if call:
        handle_call(who, where, call)

def parse_assignment(what):
    if "=" not in what:
        return False

    before, after = what.split("=",1)
    before = before.strip()
    after = after.strip()

    name = before
    args = []
    if before.endswith(")"):
        if "(" not in before:
            return False

        name, arg_str = before[:-1].split("(",1)
        name = name.strip()
        args = map(lambda x:x.strip(), arg_str.split(","))

    return {
        "name": name,
        "args": args,
        "expr": after}

def parse_call(what):
    name = what
    args = []

    if what.endswith(")"):
        if "(" not in what:
            return False
        name, arg_str = what[:-1].split("(", 1)
        args = map(lambda x:x.strip(), arg_str.split(","))
    return {"name": name.strip(), "args": args}

def handle_assignment(who, assignment):
    aliases = _ALIASES.get(who, {})
    aliases[assignment['name']] = (assignment['args'], assignment['expr'])

def handle_call(who, where, call):
    replacement = _ALIASES.get(who, {}).get(call["name"], False)
    if not replacement:
        return
    
    rep_args, rep_expr = replacement
    if len(rep_args) != len(call["args"]):
        say(where, "Argument mismatch. Provided:{}, Expected{}."
            .format(len(call["args"]), len(rep_args)))
        return

    replacement_map = dict(zip(rep_args, call["args"]))
    parts = re.split("(%s)" % "|".join(rep_args), rep_expr)
    parts[1::2] = [replacement_map[key] for key in parts[1::2]]
    rep_str = "".join(parts)
    think(":{}! PRIVMSG {} :{}".format(
        who,
        where,
        rep_str))

