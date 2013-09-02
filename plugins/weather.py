from . import *
import urllib2
import json

#Sits next to main.py
KEY = file("weather_key").read().strip()

def get_response(command):
    url = "http://api.wunderground.com/api/%s/%s.json" % (KEY, urllib2.quote(command))
    json_string = urllib2.urlopen(url).read()
    return json.loads(json_string)

@command("w")
def current_weather(who, what, where):
    weather = get_response("conditions/q/" + what.strip())
    if "results" in weather["response"]:
        say(where, "I have %s results for %s. Please be more specific. (use a zip?)" % (len(weather["response"]["results"]), what))
        if str(weather["response"]["results"][0]["state"]) == "":
            return

        states = [
            str(entry["state"])
            for entry in weather["response"]["results"]
        ]

        say(where, "States found: (%s)" % ", ".join(states))
        return
    if "current_observation" not in weather:
        say(where, "No weather there? wat.")
        return
    obs = weather["current_observation"]
    output = obs["display_location"]["full"]
    output += ": " + obs["weather"]
    output += ", " + obs["temperature_string"]
    output += " but feels like " + obs["feelslike_string"]
    output += " " + obs["observation_time"]

    say(where, output)
