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
        self.read_queues = [self.net_read._reader]
        self.write_queues = [] #don't put self.net_write here.
        #because we'll iterate though this list to broadcast messages
        self.output_listeners = []

    def load(self, plugin_name):
        """ Load a plugin """
        if plugin_name in self.plugin_map:
            return False
        plugin = Plugin(plugin_name)
        self.plugin_map[plugin_name] = plugin
        self.read_queues.append(plugin.reader())
        self.write_queues.append(plugin.writer())
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

        self.read_queues.remove(plugin.reader())
        self.write_queues.remove(plugin.writer())
        plugin.stop()
        del self.plugin_map[plugin_name]
        return True

    def cycle(self, plugin_name):
        """ Load a plugin, unloading first it if it exists. """
        self.unload(plugin_name)
        return self.load(plugin_name)
    
    def run(self):
        self.net_write.put("NICK " + self.nick)
        self.net_write.put("USER {} localhost localhost :{}"
            .format(self.nick, self.real_name))

        while True:
            readable, _, _ = select(self.read_queues, [], [])
            for readable_fd in readable:
                plugin_name = ""
                if readable_fd == self.net_read._reader:
                    readable_queue = self.net_read
                else:
                    for plugin_name, plugin in self.plugin_map.items():
                        if readable_fd == plugin.reader():
                            readable_queue = plugin
                            break
                data = readable_queue.get()
                if readable_queue == self.net_read:
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
                else: #plugin has data, put it in the net queue
                    if data is None:
                        self.unload(plugin_name)
                        continue
                    if data.startswith("::RECEIVE_OUTPUT:"):
                        if data.split(":")[-1] == "True":
                            self.output_listeners.append(plugin)
                        else:
                            self.output_listeners.remove(plugin)
                        continue
                    for p in self.output_listeners:
                        p.put(data)
                    self.net_write.put(parse_colors(data))

    def on_notice_action(self, notice_action):
        print(notice_action)
        _, action, args = notice_action
        if action in ["load", "unload", "cycle"]:
            plugins = args.split()
            cb = getattr(self, action)
            map(cb,plugins)
    def _stop(self):
        for queue in self.plugin_map.values():
            queue.put(None)

    def _ready(self):
        self.ready = True
        for queue in self.plugin_map.values():
            queue.put("::STATE:READY")

