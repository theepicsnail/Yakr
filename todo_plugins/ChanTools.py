from Hook import *

@requires("IRCArgs")
class ChanTools:
    @bindFunction(command="RPL_ENDOFMOTD")
    def autoJoin(self,response):
        yield response.join("#test")
        yield response.join("#adullam")

