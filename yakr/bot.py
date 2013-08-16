""" Yakr's main bot class.
This is responsible for tieing together the plugin manager,
the network connection, the message dispatching, etc...
"""

import networking
import plugin_manager
import gevent
#import gevent.queue

class Bot:
    """
    yakr.bot.Bot
    create a new instance of this class, configure it with
    load_config(dict) and load_plugin(name)
    then enter the main loop through run()
    """

    def __init__(self):
        self.connection = None
        self.plugin_manager = plugin_manager.PluginManager()
        self.nick = ""
        self.name = ""

    def load_config(self, config):
        """
        configure the bot with the given config dict.
        the config passed in is expected to have the format:
        {"connection":{
            "host": "someServer",
            "port": "1234",
            "ssl": "False", 
        },
        "bot":{
            "nick": "SomeIrcNick",
            "name": "Some Full Name",
        }}
        Note: port and ssl are string values.
        port and ssl are optional, by default port is "6667" 
        and ssl is "false"
        """
        assert config.has_key("connection")
        assert config["connection"].has_key("host")
        
        assert config.has_key("bot")
        assert config["bot"].has_key("nick")
        assert config["bot"].has_key("name")

        self.nick = config["bot"]["nick"]
        self.name = config["bot"]["name"]

        connection_class = None
        if config["connection"].get("ssl", "False")=="True":
            connection_class = networking.SslTcp
        else:
            connection_class = networking.Tcp

        self.connection = connection_class(
            config["connection"]["host"],
            int(config["connection"].get("port", "6667")))

    def load_plugin(self, plugin):
        """
        tell the bot to load a plugin.
        This should probably not exist as it's a bridge between
        the bot (self), and the plugin_manager.
        TODO: restructure yakr so that this bridge isn't needed.
        """
        self.plugin_manager.load(plugin)

    def run(self):
        """
        Start up entry point for yakr.
        This starts the connection as well as starts the thread
        that does the main reading/writing on the connection
        """
        job = gevent.spawn(self._main_loop)
        self.connection.connect()
        gevent.joinall([job])

    def _main_loop(self):
        """
        Main loop of yakr. This handles the simple IRC bot bits like
        responding to pings, setting up the nick and user lines.
        """
        input_queue = self.connection.get_input()
        output_queue = self.connection.get_output()
        output_queue.put("NICK " + self.nick)
        output_queue.put("USER {} localhost localhost :{}"
            .format(self.nick, self.name))

        running = True
        while running:
            msg = input_queue.get()
            if msg.startswith("PING"):
                output_queue.put("PONG" + msg[4:])
            print(">", msg)
