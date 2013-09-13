# -*- coding: utf-8 -*-
from yakr.plugin_base import *
import math
import random
import re

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
        return
    elif "table" in what:
        say(where, who + u": (╯{C4}°{}□{C4}°{}）╯{C10}︵ {C7}┻━┻{C10})")
        return
    elif "hair" in what:
        say(where, who + ": I WHIP MY HAIR BACK AND FORTH")
        return
    elif "flop" in what:
        say(where, who + ": Heads, definitely. Well, tails is nice, too. Yeah, let's go with tails. No, heads. Tails. ...which do you like?")
        return

    say(where, who + ": " + random.choice(["heads", "tails"]))

@command("roll")
def roll(who, what, where):

    if not what:
        return roll_1d6()

    else:
        try:
            roll_dict = re.match("(?P<dice>\d*)[dD](?P<sides>\d+)((?P<operator>[-+*/x])(?P<modifier>\d+))?", what).groupdict()
            roll_dict["sides"] = int(roll_dict["sides"])
        except AttributeError:
            try:
                roll_dict = re.match("(?P<dice>\d*)", what).groupdict()
                roll_dict["sides"] = 6
            except AttributeError:
                say(where, who + ": The syntax is [number of dice]d[number of sides per dice][modifier (-1, +2, *3, /4)]")
            return
        rollsults = []

        if roll_dict["sides"] > 1000000000:
            say(where, who + ": I, uh...couldn't lift the die. O.o")
            return

        elif roll_dict["sides"] < 2:
            say(where, who + ": *tch* Come on, son!")
            return

        if roll_dict["dice"] and int(roll_dict["dice"]) > 1:
            roll_dict["dice"] = int(roll_dict["dice"])
            if roll_dict["dice"] < 1:
                say(where, who + ": http://i.imgur.com/ckYyr4h.jpg")
                return
            if roll_dict["dice"] > 30:
                say(where, who + ": AIN'T NOBODY GOT TIME FOR THAT! Keep it under 30 dice. ;)")
                return
            for _ in xrange(roll_dict["dice"]):
                rollsults.append(random.randint(1, roll_dict["sides"]))

            rollsults.sort()
            roll_total = sum(rollsults)

        else:
            rollsults.append(random.randint(1, roll_dict["sides"]))
            roll_total = rollsults[0]
            say(where, who + ": " + colorizer(roll_total))
            return

        colorizer = get_colorizer(roll_dict["sides"], 1)

        if roll_dict["operator"]:
            roll_dict["modifier"] = int(roll_dict["modifier"])
            roll_total = operators[roll_dict["operator"]](roll_total, roll_dict["modifier"])
            total_colorizer = get_colorizer(
                roll_dict["sides"],
                roll_dict["dice"],
                lambda x: operators[roll_dict["inverse_operator"]](x, roll_dict["modifier"]))
        else:
            total_colorizer = get_colorizer(roll_dict["sides"], roll_dict["dice"])
            

        say(where, who + ": {} for a total of {}.".format(join(map(colorizer, rollsults)), total_colorizer(roll_total)))
        return

def averages(sides, dice):
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
            
def roll_1d6():
        say(where, who +": "+ str(random.randint(1,6)))

def subtract(x, y):
    return x - y

def add(x, y):
    return x + y

def divide(x, y):
    return x / y

def multiply(x, y):
    return x * y

operators = {
    "+": add,
    "-": subtract,
    "/": divide,
    "*": multiply,
    "x": multiply
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
