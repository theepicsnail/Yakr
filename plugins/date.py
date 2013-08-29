from . import *
import time

@command("date")
def date(who, what, where):
    say(where, time.strftime("%a, %D %T"))
