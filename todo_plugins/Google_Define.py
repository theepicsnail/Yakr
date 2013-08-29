from Hook import bindFunction, requires, prefers
from Logging import LogFile
log = LogFile("GD")
log.debug("Log start")
import sys
@requires("Google")
@prefers("Colors")
class Google_Define:
    @bindFunction(message="!gd (?P<term>[a-zA-Z ]+) ?(?P<definition>\d*)")
    def g_define(self, term, response, target, colorize, gdefine, definition):
        log.debug("g_define",term, response, target, colorize, gdefine, definition)

        d = gdefine(term.strip().replace(' ', '+'), definition) 

        if colorize:
            return response.msg(target, colorize(
                "<{C3}Google Define{}: %s [{B}%s{} of %s]>" % d))
        else:
            return response.msg(target,
                    "<Google Define: %s [%s of %s]>" % d)
