from yakr.network import simple_connect
from yakr.util import set_procname
from yakr.bot import Bot
import yakr.config as botconfig
set_procname("yakr")

config = botconfig.read("yakr.cfg")

connect_host = config["connection"]["host"]
connect_port = int(config["connection"]["port"])
nick = config["bot"]["nick"]
name = config["bot"]["name"]

b = Bot(simple_connect((connect_host, connect_port)))
b.nick = nick
b.real_name = name
b.load("fortune")
b.load("repeater")
b.load("seeSelf")
b.run()
