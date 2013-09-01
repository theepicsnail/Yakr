# pylint: disable=E0102
from . import *
from threading import Timer
import pickle
import datetime
import parsedatetime.parsedatetime as pdt

_DT_PARSER = pdt.Calendar()

ALARM_STORE = "AlarmStore.pkl"
_ALARM_CACHE = []
_NEXT_ALARM = None


def load_alarms():
    global _ALARM_CACHE, ALARM_STORE
    try:
        _ALARM_CACHE = pickle.load(file(ALARM_STORE))
    except:
        _ALARM_CACHE = []

def save_alarms():
    global _ALARM_CACHE, ALARM_STORE
    pickle.dump(_ALARM_CACHE, file(ALARM_STORE, "w"))

def parse_time(time_string):
    return datetime.datetime(*_DT_PARSER.parse(time_string)[0][:6])

def add_alarm(what, where, when):
    global _ALARM_CACHE, _NEXT_ALARM
    _ALARM_CACHE.append((when, where, what))
    _ALARM_CACHE.sort()
    schedule_alarm()
    save_alarms()
    pass 

def start():
    global _NEXT_ALARM, _ALARM_CACHE
    load_alarms()
    schedule_alarm()

def schedule_alarm():
    global _NEXT_ALARM, _ALARM_CACHE
    if not _ALARM_CACHE:
        return

    if _NEXT_ALARM:
        _NEXT_ALARM.cancel()
        if not _ALARM_CACHE:
            return #No more alarms to schedule

    next_alarm_eta = (_ALARM_CACHE[0][0] - datetime.datetime.now())\
        .total_seconds()

    _NEXT_ALARM = Timer(next_alarm_eta, check_alarm)
    _NEXT_ALARM.start()

def check_alarm():
    global _ALARM_CACHE
    if not _ALARM_CACHE:
        return #No alarms, exit.

    now = datetime.datetime.now()
    
    while now > _ALARM_CACHE[0][0]:
        say(_ALARM_CACHE[0][1], _ALARM_CACHE[0][2])
        _ALARM_CACHE.pop(0)
        if not _ALARM_CACHE:
            return #No more alarms. exit.

    schedule_alarm()

@command("alarm")
def alarm(who, what, where):
    time_string, msg = what.split("#", 1)
    alarm_time = parse_time(time_string)
    if not alarm_time:
        say(where, "I couldn't figure out how to parse '%s'" % time_string)
        return
    say(where, "Scheduled for: %s" % alarm_time)
    add_alarm(msg, where, alarm_time)
