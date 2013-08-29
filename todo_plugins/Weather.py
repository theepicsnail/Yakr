from Hook import *
from Logging import LogFile
import shelve
import urllib2
import json


log = LogFile("Weather")

KEY = "90911f1ab7b29950"

def getResponse(command):
    url = "http://api.wunderground.com/api/%s/%s.json"%(KEY,urllib2.quote(command))
    log.debug("getResponse",url)
    f = urllib2.urlopen(url)
    json_string = f.read()
    response = json.loads(json_string)
    return response

    
class Weather:
    @bindFunction(message="^!w (?P<location>.*)$")
    def currentWeather(self,response,target,location):
        weather = getResponse("conditions/q/%s"%location)
        log.debug(weather.keys())
        if weather["response"].has_key("results"):
            yield response.say(target,"I found multiple results for "\
                        +location+". Please specify the state (or use zip instead)")
            states = [str(entry["state"]) for entry in weather["response"]["results"]]
                
            yield response.say(target,"Stats found: (%s)"%", ".join(states))
            return


        obs = weather["current_observation"]
        displayString = obs["display_location"]["full"]+": "\
                      + obs["weather"] + ", " + obs["temperature_string"] \
                      + " but feels like " + obs["feelslike_string"] \
                      + " " + obs["observation_time"]
        displayString = str(displayString)
        log.debug(response.say,target,displayString)
        yield response.say(target,displayString)
