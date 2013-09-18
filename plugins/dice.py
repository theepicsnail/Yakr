# -*- coding: utf-8 -*-
from yakr.plugin_base import *
import math
import operator
import random
import re

@command("roll")
def roll_command(who, what, where):
    rolldict = parse_roll(what)

    if type(rolldict) == str:  # We've had a parsing error
        say(where, who + ": " + rolldict)
        return False

    if sanity_errors(rolldict):  # Check for stupid rolls (100 dice, etc)
        say(where, who + ": " + sanity_errors(rolldict))
        return False

    rollsults, roll_total = get_rolls(rolldict)

    colorizer, total_colorizer = get_colorizers(rolldict)

    if len(rollsults) < 2:
        say(where, who + ": {}".format(colorizer(roll_total)))
    else:
        say(where,
            who + ": {} for a total of {}.".format(
                join(map(colorizer, rollsults)),
                total_colorizer(roll_total)))

    return

def parse_roll(rollstring):
    """Takes a string.
    If it finds valid dice notation or an empty string, it returns a
    dict describing the rolls to make. Otherwise, it complains and exits"""
    if not rollstring:
        return {"dice": 1, "sides": 6, "operator": None, "modifier": None}

    try:
        rolldict = re.match("(?P<dice>\d*)([dD](?P<sides>\d+)((?P<operator>[-+*/x])(?P<modifier>\d+))?)?", rollstring).groupdict()
        if not rolldict["sides"]:  #We default to a d6 when people !roll 4
            rolldict["sides"] = 6
        else:
            rolldict["sides"] = int(rolldict["sides"])  # We're going to want to use these as ints
        if not rolldict["dice"]:
            rolldict["dice"] = 1
        else:
            rolldict["dice"] = int(rolldict["dice"])
        if rolldict["operator"]:
            rolldict["modifier"] = int(rolldict["modifier"])
    except:
        return "Either use no argument, tell me the number of 6-sided dice to roll, or [number of dice]d[number of sides per dice][modifier (-1, +2, *3, /4)]:"
    else:
        return rolldict


def sanity_errors(rolldict):
    # Check the arguments for sanity
    if rolldict["sides"] > 1000000000:  # Silly huge dice
        return "I, uh...couldn't lift the die. O.o"

    elif rolldict["sides"] < 2:  # no point in rolling a d1
        return "*tch* Come on, son!"

    if rolldict["dice"] < 1:
        return "http://i.imgur.com/ckYyr4h.jpg"

    if rolldict["dice"] > 30:
        return "AIN'T NOBODY GOT TIME FOR THAT! Keep it under 30 dice. ;)"

    return

def get_rolls(rolldict):
    """Just sticks all the rolls into an array. Returns that and the sum."""

    rollsults = []  # To store the roll results

    for _ in xrange(rolldict["dice"]):
        rollsults.append(random.randint(1, rolldict["sides"]))
        #rollsults.sort()

    return rollsults, sum(rollsults)

def averages(dice, sides):
    """ The formula is a combination of the mean roll
        (number of dice times (number of sides + 1) / 2)
    and the stddev, using this variance function:
        https://en.wikipedia.org/wiki/Variance?oldid=572981218#Fair_die"""
    low = dice*((sides+1)/2)-math.sqrt(dice*((sides**2-1)/12))/2
    high = dice*((sides+1)/2)+math.sqrt(dice*((sides**2-1)/12))/2
    return low, high

def get_colorizer(sides, dice, modifier=lambda x: x):
    """Given a number of sides per die, the number of dice, and an optional
    modifier, returns a function for coloring based on how "good" the roll was."""
    avgs = map(modifier, averages(sides, dice))
    def colorizer(roll):
        if roll <= avgs[0]:
            return "{{C4}}{}{{}}".format(roll)
        elif roll <= avgs[1]:
            return "{{C8}}{}{{}}".format(roll)
        else:
            return "{{C9}}{}{{}}".format(roll)

    return colorizer

def get_colorizers(rolldict):
    """This returns 2 functions, one for coloring the individual die rolls,
    one for coloring the total. You can't easily derive how good the total
    is based on how good the individual rolls are, due to the bell curve
    tightening as you increase the number of dice.

    Also, this is probably as good a place as any to describe wtf's going on
    with this operators[]() business. So, a common feature in gaming dice rolls
    is the modifier. 1d4+1. operators is a dict that maps the string "+" with
    a function that can be used to do that function. I can't use the infix
    functions directly, so this is what I'm stuck with.

    inverse_operators[] should be self-explanatory.
    "-" -> add(), "*" -> divide(), etc.

    The reason I need them is because they alter the total, which means they
    need to be taken into account for the colorization."""
    d = rolldict["dice"]
    s = rolldict["sides"]

    colorizer = get_colorizer(1, s)

    if rolldict["operator"]:
        op = rolldict["operator"]
        mod = rolldict["modifier"]
        roll_total = operators[op](roll_total, mod)
        total_colorizer = get_colorizer(d, s,
            lambda x: inverse_operators[op](x, mod))
    else:
        total_colorizer = get_colorizer(d, s)

    return colorizer, total_colorizer

operators = {
    "+": operator.add,
    "-": operator.sub,
    "/": operator.div,
    "*": operator.mul,
    "x": operator.mul
}

inverse_operators = {
    "+": operators["-"],
    "-": operators["+"],
    "/": operators["*"],
    "*": operators["/"],
    "x": operators["/"],
}

def join(x):
    if len(x) <= 2:
        return ' and '.join(x)
    else:
        return ', '.join(x[:-1] + ['and ' + x[-1],])
