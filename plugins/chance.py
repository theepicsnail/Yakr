# -*- coding: utf-8 -*-
from yakr.plugin_base import *
import random

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
    say(where, random.choice(_MAGIC_8_OUTPUTS))

@command("flip")
def flip(who, what, where):
    if "burger" in what:
        say(where, who + ": {C4}*sizzle*{} Would you like fries with that?")
    elif "table" in what:
        say(where, who + u": (╯{C4}°{}□{C4}°{}）╯{C10}︵ {C7}┻━┻{C10})")
    elif "hair" in what:
        say(where, who + ": I WHIP MY HAIR BACK AND FORTH")
    elif "flop" in what:
        say(where, who + ": Heads, definitely. Well, tails is nice, too. Yeah, let's go with tails. No, heads. Tails. ...which do you like?")
    else:
        say(where, who + ": " + random.choice(["heads", "tails"]))
