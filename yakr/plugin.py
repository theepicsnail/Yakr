""" plugin tools
the class Plugin is used by the main process as a handle on the launched 
plugins. Plugins are started in separate processes, this serves to do the
launching though multiprocess, setting up pipes, etc..
"""
from .util import named_runner
import multiprocessing
try:
    import Queue
except ImportError:
    import queue as Queue
import signal 
import sys

class Plugin(object):
    """
    Plugin class is used in the main process as a handle to keep track
    of the launched processes.
    """

    def __init__(self, name):
        self.name = name
        self.read_pipe = multiprocessing.Queue(100)
        self.write_pipe = multiprocessing.Queue(100)
        self.proc = multiprocessing.Process(
            target = named_runner(_process_begin),
            name = name,
            args = (name, (self.write_pipe, self.read_pipe)))
        self.proc.start()

    def stop(self):
        """
        Send the sentnal value to the process to stop it.
        This does not forcefully shut down the plugin.

        if a plugin hangs during shut down, it will need to be killed

        TODO: look into scheduling a kill, so that if the process is up after
        x seconds, we forcefully kill it.
        """
        self.write_pipe.put(None)
        self.write_pipe.close()
        self.proc.join(3)
        self.proc.terminate()

    def fileno(self):
        """ 
        Returns the underlying selectable object associated with the read queue
        """
        return self.read_pipe._reader.fileno()

    def put(self, line):
        """
        Send a line to the plugin
        if the queue is full, the line is dropped
        """
        try:
            self.write_pipe.put(line, False)
        except Queue.Full:
            pass

    def get(self):
        """
        receive a line from the plugin
        if the queue is empty, false is returned

        If the output is None, this is a signal that the plugin has finished
        """
        try:
            return self.read_pipe.get(False)
        except Queue.Empty:
            return False


def _process_begin(plugin_name, data_in_data_out):
    """
    When a new process is started to launch a plugin, this is the entry point.

    plugin_name - the plugin to load
    data_in -  get() only queue of irc lines (\r\n stripped)
    data_out - put(...) only queue of irc lines (no \r\n needed)
    """
    print("starting {}".format(plugin_name))
    try:
        plugin_module = __import__("plugins." + plugin_name)
    except:
        import traceback
        traceback.print_exc()
        return
    #foo.bar.baz we want a handle on 'baz', not 'plugins'
    for sub_module in plugin_name.split("."):
        plugin_module = getattr(plugin_module, sub_module)

    """
    plugin_module should have the following methods:
    start() - called when the plugin should do it's setup/heavy lifting
    handle_line() - called when a line is received from the main process
    ready() - called when the bot signifies it's ready to send messages
    stop() - called when the bot is shutting down

    templates of each of these are provided in the __init__ in plugins, so a
    from . import *
    is enough to get you everything you need
    """

    #kill -s INT <pid>
    #will stop the plugin with that pid, gracefully.
    #this is also called when the plugin receives the end of queue value (None)
    def stop_plugin(signalno=None, frame=None):
        """ 
        stop the plugin gracefully 
        TODO: schedule some forceful kill if plugin_module.stop doesn't return
        quickly.
        """
        print("stopping {}".format(plugin_name))
        plugin_module.stop()
        data_out.put(None)
        import os
        os._exit(0)
    signal.signal(signal.SIGINT, stop_plugin)

    # let the plugin doing any initialization
    # out_queue is None here, to prevent any bot actions during start
    plugin_module.start()

    data_in, data_out = data_in_data_out
    #Read data from the main process, handling state change and sental values 
    while True:
        data = data_in.get()
        if data == "::STATE:READY": 
            #non-irc message to signify bot has entered ready mode
            #when we enter ready mode, the out_queue is now reliably being 
            #consumed, and we're connected to the server. So we're... ready
            plugin_module.set_out_queue(data_out)
            plugin_module.ready()
            #This isn't an IRC message, don't give it to handle_line
            continue

        if data is None: #end of queue signal from main process. end the plugin
            stop_plugin()
            sys.exit(0)

        try:
            plugin_module.handle_line(data)
        except:
            import traceback
            traceback.print_exc()
            
