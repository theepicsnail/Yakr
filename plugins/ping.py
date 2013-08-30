from . import *
import socket
import subprocess
from thread import start_new_thread

@command("ping")
def ping(who, what, where):
     start_new_thread(pinger, (what, where))

def parse_time(line):
    return float(line.split("=")[-1].split(" ")[0])

def avg(times):
    return sum(times)/len(times)

def color_time(time):
    c = 4
    if time < 50:
        c = 8
    if time < 10:
        c = 3
    return "{C%s}%s{}" % (c, time)

def pinger(host, chan):
    say(chan, "pinging " + host)
    try:
        addr_info = socket.getaddrinfo(host, 1, 0, 0, socket.SOL_TCP)
        if not addr_info:
            raise Exception("") #Failed to resolve to an ip.
        ip = addr_info[0][-1][0]
        say(chan, "resolved to {}". format(ip))

        out = subprocess.check_output(["ping", "-c", "5", host])
        lines = out.split("\n")[1:6]
        if not lines[0]:
            say(chan, "Host didn't reply :(")
            return

        avg_time = avg(map(parse_time, lines))
        say(chan, "{}({}): {} ms".format(host, ip, color_time(avg_time)))
        
    except:
        say(chan, "Could not resolve " + host)
        raise
