from Hook import *
parser = None
from Logging import LogFile
log = LogFile("Alarm")
import time
import datetime


storeFile = "AlarmStore.pkl"
parseStrings = [
"%m/%d",
"%m/%d/%y",
"%m/%d/%y %H:%M:%S",
"%m/%d/%y %h:%M:%S %p"
]
def backupParse(s):
    global parseStrings
    for fmt in parseStrings:
        try:
            return datetime.datetime.strptime(s,fmt)
        except:pass
    return None

try:
    import parsedatetime.parsedatetime as pdt
    import parsedatetime.parsedatetime_consts as pdc
    c = pdc.Constants()
    p = pdt.Calendar(c)
    parser = lambda s:datetime.datetime(*p.parse(s)[0][:6])
    log.debug("Using parsedatetime")
except:
    parser = backupParse
    log.debug("Using backup parser")

try:
    import cPickle as pickle
    log.debug("Using cPickle")
except:
    import pickle
    log.debug("Using pickle.")


def saveAlarms(alarms):
    try:
        log.debug("Saving alarms",storeFile,alarms)
        pickle.dump(alarms,file(storeFile,"w"))
        log.debug("saved.")
    except:
        log.exception("Failed to store pickle.")
def loadAlarms():
    try:
        log.debug("Loading alarms", storeFile)
        alarms = pickle.load(file(storeFile))
        log.debug("Loaded.", alarms)
        return alarms;
    except:
        log.exception("Failed to load pickle")
        return False




@requires("IRCArgs")
class Alarm:
    def __init__(self):
        self.alarms = loadAlarms()
        if self.alarms == False:
            self.alarms = []

    @dedicated(delay=1)
    def ded(self,response):
        if not self.alarms:
            log.debug("No alarms to fire.")
            return
        moreAlarms = True
        while moreAlarms:
            moreAlarms = False
            now = datetime.datetime.now()
            curAlarm = self.alarms[0]
            if now > curAlarm[0]:
                moreAlarms = True
                log.debug("Firing alarm:",*curAlarm) 
                yield response.msg(curAlarm[1],curAlarm[2])
                self.alarms.pop(0)
                saveAlarms(self.alarms)

    @bindFunction(message="!alarm (?P<when>.*?)#(?P<what>.*)")
    def sched(self,response,target,when,what):
        log.debug("Scheduler triggered.")
        dt = parser(when)
        if not dt:
            log.warning("Invalid time.",when)
            yield response.msg(target,"Sorry, I couldn't figure out when \"%s\" is."%when)
            return
        log.debug("Scheduled alarm:",when,target,what)
        yield response.msg(target,"Sceduled for: %s"%dt)
        self.alarms.append((dt,target,what))
        self.alarms.sort()
        saveAlarms(self.alarms)
    
