from . import *
import random

@command("choose")
def choose(who, what, where):
    say(where, random.choice(what.split("or")))

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


@command("roll")
def roll(who, what, where):
    say(where, who +": "+ str(random.randint(1,6)))
