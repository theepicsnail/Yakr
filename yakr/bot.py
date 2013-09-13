"""
plugin manager stores a map of all the loaded plugins and does some of the
queue management.
"""
from .util import parse_colors
from .plugin import Plugin
from select import select
import re

_NOTICE_RE = re.compile(":([^ ]+)![^ ]+ NOTICE [^ ]+ :([^ ]+) ?(.*)")

class Bot(object):
    """Yakr bot class. """
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
        """Get the list of readable queues"""
        # pylint: disable=W0212, C0301
        #http://stackoverflow.com/questions/1123855/select-on-multiple-python-multiprocessing-queues
        return self.plugin_map.values() + [self.net_read._reader]

    def run(self):
        """main entry point of the bot"""
        self.net_write.put("NICK " + self.nick)
        self.net_write.put("USER {} localhost localhost :{}"
            .format(self.nick, self.real_name))

        while True:
            readable, _, _ = select(self.get_readables(), [], [])
            for readable_fd in readable:
                if type(readable_fd) is Plugin:
                    self.handle_plugin_read(readable_fd)
                else:
                    self.handle_net_read()

    def handle_plugin_read(self, plugin):
        """Handle a plugin that is ready to read"""
        data = plugin.get()
        if data is None:
            self.unload(plugin.name)
            return

        if data.startswith("::"):
            data = data[2:]
            if data.startswith("RECEIVE_OUTPUT:"):
                if data.split(":")[-1] == "True":
                    self.output_listeners.append(plugin)
                else:
                    self.output_listeners.remove(plugin)
            elif data.startswith("REPROCESS:"):
                data = data[10:]
                self.process_net_data(data)
            return

        self.broadcast(data)

    def broadcast(self, data):
        """Send a line to the net and all plugins interested"""
        #Raw line to any listeners
        for out_queue in self.output_listeners:
            out_queue.put(data)
        #Parse it and send it to the net
        self.net_write.put(parse_colors(data))

    def handle_net_read(self):
        """Handle when the net has data for the bot"""
        data = self.net_read.get()
        if data is None:
            self._stop()
            return
        self.process_net_data(data)

    def process_net_data(self, data):
        print "process:", data
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
        """When the bot is sent a notice for action"""
        print("Admin action: {}".format(notice_action))
        who, action, args = notice_action
        if action in ["load", "unload", "cycle"]:
            plugins = args.split()
            callback = getattr(self, action)
            for plugin_name in plugins:
                callback(plugin_name)

        elif action == "part":
            rooms = args.split()
            self.net_write.put("PART {} {}".format(
                    ",".join(rooms),
                    "Parted by " + who))
        elif action == "quote":
            self.net_write.put(args)
    def _stop(self):
        """Send the stop signal to all of the plugins"""
        for queue in self.plugin_map.values():
            queue.put(None)

    def _ready(self):
        """Send the ready signal to all of the plugins"""
        self.ready = True
        for queue in self.plugin_map.values():
            queue.put("::STATE:READY")

