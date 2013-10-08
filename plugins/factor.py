from yakr.plugin_base import *
import subprocess

@command("factor")
def date(who, what, where):
    i = int(what)
    out = subprocess.check_output(["factor", str(i)])
    say(where, out.strip())
