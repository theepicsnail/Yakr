from yakr.network import simple_connect, record, replay
from yakr.util import set_procname
from yakr.bot import Bot
import yakr.config as botconfig
import sys
import os
import re
config = botconfig.read("yakr.cfg")

set_procname(config.get("bot.process", "yakr"))

blacklist = config.get("plugin.blacklist", "^$").split(" ")
whitelist = config.get("plugin.whitelist", "^.*$").split(" ")
def plugin_filter(f):
    return f.endswith(".py") and not f.startswith("_")
def passes_white_black_lists(plugin):
    for regex in whitelist:
        if re.match(regex, plugin):
            break
    else:
        print "'{}' wasn't on the whitelist".format(plugin)
        return False

    for regex in blacklist:
        if re.match(regex, plugin):
            print "'{}' was on the blacklist (re: '{}')".format(plugin, regex)
            return False
    return True


plugins = []
for name, dirs, files in os.walk("plugins"):
    files = filter(plugin_filter, files)
    plugin_path = name.split("/")[1:]
    for f in files:
        plugin = ".".join(plugin_path+[f[:-3]])
        
        if passes_white_black_lists(plugin):
            plugins.append(plugin)
print "Detected", len(plugins), "plugin(s)."



connect_host = config.get("connection.host", False)
connect_port = config.get("connection.port", False)
nick = config.get("bot.nick", False)
name = config.get("bot.name", "Unnamed bot")
if [connect_host, connect_port, nick].count(False):
    print "Minimum requirements for a config file:"
    print "[connection]"
    print "host = SOME_HOST"
    print "port = SOME_PORT"
    print "[bot]"
    print "nick = SOME_NICK"
    exit(1)
connect_port = int(connect_port)

net = None
if len(sys.argv) >= 2:
    if sys.argv[1] == "record":
        conn = simple_connect((connect_host, connect_port))
        net = record(conn, "RECORD")
    if sys.argv[1] == "replay":
        net = replay("RECORD")
    if sys.argv[1] == "test":
        import unittest
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests'))
        exit_code = 0
        if result.failures:
            exit_code += 1
        if result.errors:
            exit_code += 2
        exit(exit_code)
    if sys.argv[1] == "plugin":
        import yakr.plugin_maker
        yakr.plugin_maker.interactive()
        exit(0)
else:
    net = simple_connect((connect_host, connect_port))

b = Bot(net)
b.nick = nick
b.real_name = name
map(b.load, plugins)
b.run()
