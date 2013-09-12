from yakr.plugin_base import *


colors = ["{C0}", "{C4}", "{C7}", "{C3}", "{C10}", "{C6}"]
clen = 6
level = 0

def up():
    global level
    level = (level + 1)%clen

def down():
    global level
    level = (level + clen-1) %clen

@command("colorize")
def colorize(who, what, where):
    global level
    level = 0
    out = colors[0]
    for i in what:
        if i == "(":
            out += "("
            up()
            out += colors[level]
        elif i == ",":
            down()
            out += colors[level] + ","
            up()
            out += colors[level]
        elif i == ")":
            down()
            out += colors[level] + ")"
        else:
            out += i
    say(where, out)


@command("colors")
def colors_cmd(who, what, where):
    say(where, " ".join(["{C%s}%s"%(s,s) for s in range(16)]))
