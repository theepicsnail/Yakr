"""
plugin manager stores a map of all the loaded plugins and does some of the
queue management.
"""
from .util import parse_colors
from .plugin import Plugin
from select import select
import re
try:
    import Queue
except ImportError:
    import queue as Queue

_NOTICE_RE = re.compile(":([^ ]+)![^ ]+ NOTICE [^ ]+ :([^ ]+) ?(.*)")

class Bot(object):

    def __init__(self, network_queues):
        self.net_write, self.net_read = network_queues
        self.ready = False
        self.nick = "Dot"
        self.real_name = "Dot the bot"
        self.plugin_map = {}
        self.output_listeners = []

    def load(self, plugin_name):
        """ Load a plugin """
        if plugin_name in self.plugin_map:
            return False
        plugin = Plugin(plugin_name)
        self.plugin_map[plugin_name] = plugin
        if self.ready:
            plugin.put("::STATE:READY")
        return True

    def unload(self, plugin_name):
        """ Unload a plugin """
        if plugin_name not in self.plugin_map:
            return False
        plugin = self.plugin_map[plugin_name]
        if plugin in self.output_listeners:
            self.output_listeners.remove(plugin)

        plugin.stop()
        del self.plugin_map[plugin_name]
        return True

    def cycle(self, plugin_name):
        """ Load a plugin, unloading first it if it exists. """
        self.unload(plugin_name)
        return self.load(plugin_name)
    
    def get_readables(self):
        return self.plugin_map.values() + [self.net_read._reader]

    def run(self):
        self.net_write.put("NICK " + self.nick)
        self.net_write.put("USER {} localhost localhost :{}"
            .format(self.nick, self.real_name))

        while True:
            readable, _, _ = select(self.get_readables(), [], [])

            for readable_fd in readable:
                if readable_fd == self.net_read._reader:
                    self.handle_net_read()
                else:
                    self.handle_plugin_read(readable_fd)

    def handle_plugin_read(self, plugin):
        data = plugin.get()
        if data is None:
            self.unload(plugin.name)
            return

        if data.startswith("::RECEIVE_OUTPUT:"):
            if data.split(":")[-1] == "True":
                self.output_listeners.append(plugin)
            else:
                self.output_listeners.remove(plugin)
            return

        self.broadcast(data)

    def broadcast(self, data):
        #Raw line to any listeners
        for out_queue in self.output_listeners:
            out_queue.put(data)
        #Parse it and send it to the net
        self.net_write.put(parse_colors(data))

    def handle_net_read(self):
        data = self.net_read.get()
        if data is None:
            self._stop()
            return
        if data.startswith("PING"):
            self.net_write.put("PONG" + data[4:])
        if ("001 %s :" % self.nick) in data:
            self._ready()
        notice_action = _NOTICE_RE.match(data)
        if notice_action:
            self.on_notice_action(notice_action.groups())
        for queue in self.plugin_map.values():
            queue.put(data)

    def on_notice_action(self, notice_action):
        print(notice_action)
        who, action, args = notice_action
        if action in ["load", "unload", "cycle"]:
            plugins = args.split()
            cb = getattr(self, action)
            map(cb,plugins)
        elif action == "part":
            rooms = args.split()
            for room in rooms:
                self.net_write.put("PART {} {}".format(
                    ",".join(rooms),
                    "Parted by " + who))
    def _stop(self):
        for queue in self.plugin_map.values():
            queue.put(None)

    def _ready(self):
        self.ready = True
        for queue in self.plugin_map.values():
            queue.put("::STATE:READY")

