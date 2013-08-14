import networking
import plugin_manager
import gevent
import gevent.queue

class Bot:
    def __init__(self):
        self.connection = None
        self.plugin_manager = plugin_manager.PluginManager()

    def load_config(self, config):
        assert config.has_key("connection")

        connectionClass = None
        if config["connection"].get("ssl", "False")=="True":
            connectionClass = networking.SslTcp
        else:
            connectionClass = networking.Tcp

        self.connection = connectionClass(
            config["connection"]["host"],
            int(config["connection"].get("port", "6667")))

    def load_plugin(self, plugin):
        self.plugin_manager.load(plugin)

    def run(self):
        print(self.plugin_manager.plugin_map)
        job = gevent.spawn(self._main_loop)
        self.connection.connect()
        gevent.joinall([job])
        pass

    def _main_loop(self):
        input_queue = self.connection.get_input()
        output_queue = self.connection.get_output()
        output_queue.put("NICK Dot")
        output_queue.put("USER Dot localhost localhost :Dot the bot")
        running = True
        while running:
            msg = input_queue.get()
            if msg.startswith("PING"):
                output_queue.put("PONG" + msg[4:])
            print("msg", msg)



#pluginHandler should be set before any of: on, off, after, every are called
#The pluginHandler provides:
#enableHook, disableHook, createMessageHook, createTimeHook, cmd
_pluginHandler = None

def setPluginHandler(handler):
  global _pluginHandler
  _pluginHandler = handler

def getPluginHandler():
  global _pluginHandler
  assert _pluginHandler is not None, "No plugin handler has been set."
  return _pluginHandler

def send(target, msg):
  getPluginHandler().cmd('PRIVMSG', (target + ' :' + msg))

def join(room):
  getPluginHandler().cmd('JOIN', room)

def on(regex, callback=None, messageType=None):
  """
    Create (or re-enable) a hook.
    on(descriptor) => descriptor
      renable the hook associated with that descriptor
      returns the descriptor passed in

    on(regex, callback) => descriptor
      creates a new hook that listens for a PRIVMSG that matches the regex
      upon a match, the callback is called.
    
    on(regex, callback, messageType) => descriptor
      Same as above but lets you specify 
  """
  if callback is None: 
    if messageType is None:
      #on(x), assert x is an int.
      assert type(regex)==int, "on(descriptor) requires an integer descriptor"
      getPluginHandler().enableHook(regex)
      return regex # on(...) always returns the descriptor we turned on. 

    else:
      #on(x, None, y)
      #on(x, messageType=y)
      assert False, "Callback must be provided to on(regex, callback, type)"

  else:
    if messageType is None:
      #on(x, y) == on(x, y, "PRIVMSG")
      messageType = "PRIVMSG"
    desc = getPluginHandler().createMessageHook(regex, callback, messageType)
    getPluginHandler().enableHook(desc)
    return desc

def off(desc):
  getPluginHandler().disableHook(desc)
  return desc

def every(seconds, callback):
  desc = getPluginHandler().createTimeHook(seconds, callback, True)
  return desc

def after(seconds, callback):
  desc = getPluginHandler().createTimeHook(seconds, callback, False)
  return desc

