# -*- coding: utf-8 -*-
from yakr.plugin_base import *
import math
import operator
import random
import re

@command("roll")
def roll(who, what, where):

    if not what:
        return say(where, who +": "+ get_colorizer(1,6)(random.randint(1,6)))

    try:
        roll_dict = re.match("(?P<dice>\d*)([dD](?P<sides>\d+)((?P<operator>[-+*/x])(?P<modifier>\d+))?)?", what).groupdict()
        if not roll_dict["sides"]:
            roll_dict["sides"] = 6
        else:
            roll_dict["sides"] = int(roll_dict["sides"])
        if not roll_dict["dice"]:
            roll_dict["dice"] = 1
        else:
            roll_dict["dice"] = int(roll_dict["dice"])
    except:
        say(where, who + ": Either use no argument, tell me the number of 6-sided dice to roll, or [number of dice]d[number of sides per dice][modifier (-1, +2, *3, /4)]:")
        return

    rollsults = []

    if roll_dict["dice"] > 1:
        roll_dict["dice"] = int(roll_dict["dice"])

    if sanity_errors(roll_dict):
        say(where, who + sanity_errors(roll_dict))

    for _ in xrange(roll_dict["dice"]):
        rollsults.append(random.randint(1, roll_dict["sides"]))

        rollsults.sort()
        roll_total = sum(rollsults)

    if roll_dict["dice"] == 1:
        rollsults.append(random.randint(1, roll_dict["sides"]))
        roll_total = rollsults[0]
        colorizer = get_colorizer(1, roll_dict["sides"])
        return say(where, who + ": " + colorizer(roll_total))

    colorizer = get_colorizer(1, roll_dict["sides"])

    if roll_dict["operator"]:
        roll_dict["modifier"] = int(roll_dict["modifier"])
        roll_total = operators[roll_dict["operator"]](roll_total, roll_dict["modifier"])
        total_colorizer = get_colorizer(
            roll_dict["dice"],
            roll_dict["sides"],
            lambda x: operators[roll_dict["inverse_operator"]](x, roll_dict["modifier"]))
    else:
        total_colorizer = get_colorizer(roll_dict["dice"], roll_dict["sides"])


    say(where, who + ": {} for a total of {}.".format(join(map(colorizer, rollsults)), total_colorizer(roll_total)))
    return


def sanity_errors(roll_dict):
    # Check the arguments for sanity
    if roll_dict["sides"] > 1000000000:  # Silly huge dice
        return ": I, uh...couldn't lift the die. O.o"

    elif roll_dict["sides"] < 2:  # no point in rolling a d1
        return ": *tch* Come on, son!"

    if roll_dict["dice"] < 1:
        return ": http://i.imgur.com/ckYyr4h.jpg"

    if roll_dict["dice"] > 30:
        return ": AIN'T NOBODY GOT TIME FOR THAT! Keep it under 30 dice. ;)"

    return

def averages(dice, sides):
    # The formula is a combination of the mean roll (number of dice times (number of sides + 1) / 2) and
    # the stddev, using this variance function: https://en.wikipedia.org/wiki/Variance#Fair_die
    low = dice*((sides+1)/2)-math.sqrt(dice*((sides**2-1)/12))
    high = dice*((sides+1)/2)+math.sqrt(dice*((sides**2-1)/12))
    return low, high

def get_colorizer(sides, dice, modifier=lambda x: x):
    avgs = map(modifier, averages(sides, dice))
    def colorizer(roll):
        if roll <= avgs[0]:
            return "{{C4}}{}{{}}".format(roll)
        elif roll <= avgs[1]:
            return "{{C8}}{}{{}}".format(roll)
        else:
            return "{{C9}}{}{{}}".format(roll)

    return colorizer
            
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
