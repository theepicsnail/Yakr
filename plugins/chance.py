# -*- coding: utf-8 -*-
from yakr.plugin_base import *
import random

def chooser(items):
    return random.choice(items)

@command("choose")
def choose(who, what, where):
    say(where, random.choice(what.split(" or ")))

_MAGIC_8_OUTPUTS = [
    "As I see it, yes",
    "It is certain",
    "It is decidedly so",
    "Most likely",
    "Outlook good",
    "Signs point to yes",
    "Without a doubt",
    "Yes",
    "Yes - definitely",
    "You may rely on it",
    "Reply hazy, try again",
    "Ask again later",
    "Better not tell you now",
    "Cannot predict now",
    "Concentrate and ask again",
    "Don't count on it",
    "My reply is no",
    "My sources say no",
    "Outlook not so good",
    "Very doubtful"]

@command("8")
def magic8(who, what, where):
    say(where, chooser(_MAGIC_8_OUTPUTS))

_FLIP_EGGS = {
    "burger":"{C4}*sizzle*{} Would you like fries with that?",
    "table": u"(╯{C4}°{}□{C4}°{}）╯{C10}︵ {C7}┻━┻{C10})",
    "hair": "I WHIP MY HAIR BACK AND FORTH",
    "flop": ("Heads, definitely. Well, tails is nice, too. "
             "Yeah, let's go with tails. "
             "No, heads. Tails. ...which do you like?")
}
@command("flip")
def flip(who, what, where):
    msg = who + ": "
    if what in _FLIP_EGGS:
        msg += _FLIP_EGGS[what]
    else:
        msg += chooser(["heads", "tails"])

    say(where, msg)
