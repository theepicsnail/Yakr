from . import *
from random import sample, randint
import re, urllib
from collections import Counter

def ready():
    receiveSelfOutput(True)

_LARGE_VALUES = [25, 50, 75, 100]
_SMALL_VALUES = range(1, 11) * 2
CURRENT_GAME = None
CURRENT_WINNER = (None, 999)
#Sets up a new game, (or sets CURRENT_GAME to None if invalid config)
def create_game(large_count):
    global CURRENT_GAME, CURRENT_WINNER
    CURRENT_WINNER = (None, 0)
    if 0 > large_count or large_count > 4:
        CURRENT_GAME = None
        return
    bigs = sample(_LARGE_VALUES, large_count)
    smalls = sample(_SMALL_VALUES, 6-large_count)
    goal = randint(100, 900)

    CURRENT_GAME = (bigs + smalls, goal)

def game_state():
    if CURRENT_WINNER[0] is None:
        return "No winner"
    score_color = 4
    if CURRENT_WINNER[1] <= 10:
        score_color = 8
    if CURRENT_WINNER[1] <= 1:
        score_color = 3
    return "Winner: {{C3}}{}{{}} with a score of {{C{}}}{}".format(
        CURRENT_WINNER[0], score_color, CURRENT_WINNER[1])

def end_game():
    global CURRENT_GAME, CURRENT_WINNER
    CURRENT_GAME = None
    CURRENT_WINNER = (None, 0)

def solve():
    game = CURRENT_GAME
    url = "http://djce.org.uk/countdown?n="+"&n=".join(map(str,game[0]))+"&t="+str(game[1])
    return urllib.urlopen(url).read().split("\n</pre>")[0].split("\n")[-1]

_EQUATION_CACHE = {}
def validate_equation(who):
    equ = _EQUATION_CACHE[who]
    nums = re.findall("[0-9]+", equ)
    used = Counter(map(int, nums))
    return used - Counter(CURRENT_GAME[0])


#Listen for maths.py's output e.g. "snail: 1.2"
@match("^PRIVMSG (.*) :(.*): ([0-9\-\.]+)$")
def on_result(groups):
    global CURRENT_WINNER
    where, who, value = groups
    if not CURRENT_GAME:
        return

    try:
        bad_nums = validate_equation(who)
        if bad_nums:
            say(where, "Bad numbers: {}".format(list(bad_nums.elements())))
            return

        score = abs(CURRENT_GAME[1] - float(value))
        if not value.endswith(".0"):
            say(where, "Answer must be an integer.")
            return

        if CURRENT_WINNER[0] == None or score < CURRENT_WINNER[1]:
            CURRENT_WINNER = (who, score)
            say(where, "Current " + game_state())
        if score == 0:
            say(where, "Game over. " + game_state())
            end_game()
    except:
        raise

#List for users equation inputs e.g. "%6/5"
@privmsg
def check_equation(who, what, where):
    if not what.startswith("%"):
        return
    _EQUATION_CACHE[who] = what[1:]    


@command("numbers")
def numbers_main(who, what, where):
    if what == "":
        if CURRENT_GAME is not None:
            say(where, str(CURRENT_GAME) + " " + game_state())
        else:
            say(where, "No active game.")
        return

    if what in "01234":
        if CURRENT_GAME != None:
            say(where, "Game over. " + game_state())
        create_game(int(what))
        if CURRENT_GAME is not None:
            say(where, "New game: {}".format(CURRENT_GAME))
        return
    
    if what == "solve":
        if CURRENT_GAME is None:
            say(where, "No active game.")
            return
        say(where, "Answer: " + solve())
        say(where, "Game over. " + game_state())
        return

    say(where, " ".join([
        "'!numbers' to show current state.",
        "'!numbers 0-4' to start a new game.",
        "'!numbers solve' to solve the current game."]))
