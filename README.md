Yakr is yet another IRC bot. This one is designed to be very thin, with the same plugability of Superbot and Superbot2.

[![Build status](https://travis-ci.org/theepicsnail/Yakr.png)](https://travis-ci.org/theepicsnail/Yakr)
### Starting

To **start** the bot:
(Be sure to configure the bot first!)

    python Main.py

To **configure** the bot:
Edit yakr.cfg
To change the plugins that are loaded, you need to edit Main.py (Issue: #2 )


### Managing Yakr

Commands are sent to yakr through notices.

/notice <bot> <command> <space separated arg list>
where <bot> is your bots name
valid commands:

    load - load each plugin (skipping if loaded already)
    unload - unload each plugin
    cycle - load each plugin (unloading first if necessary)
    quote - have yakr send the argument unaltered to the network
    part - have yakr leave channels


### Writing plugins

Create your plugin under the **plugins** directory.
The name of your plugin will be the module name for your file (wihout 'plugins.')

    plugins/foo.py -> "foo"
    plugins/my_plugins/bar.py -> "my_plugins.bar"

Start your python file off with 

    from yakr.plugin_base import *
    
You're now ready to add your plugin functionality. See **Plugin Life** and **Plugin Base** for more information.

### Debugging plugins

Yakr comes with 2 modes that help make debugging a plugin easier/quicker.

    python main.py record
    
Will record all (Issue: #3 ) network traffic to/from the bot into a RECORD file. 
Reproduce your plugin failing in record mode to capture it. Once captured you can:

    python main.py replay

Which will play back the recorded data, allowing you to test your plugin against the example over and over. 
This prevents you from needing to connect the bot to the irc server each test. 
Editing the RECORD file lets you change your test example without needing to connect to the irc server too.

Exceptions are logged to **#test**, and the stack traces are shown in stdout, which may help you debug your issues.

There are a couple plugins that may prove useful too.

    stdout - print network data to stdout
    sprunge - record a number of lines, and then upload them to sprunge


### Plugin Life

This section explains the stages a plugin can go through and what's available at each stage.
Within a plugin, there is only one thread (unless you create some for yourself)

* Your process is started (by yakr)
* Your plugin is loaded 
    * If loading fails, skip to stop()
* start() is called
    * At this point most plugin features will not work
    * This space is where heavy initial code should go
* The plugin enters its main loop now
* Each line is processed (more about this step below)
* Eventually ready() gets called
    * At this point, all plugin features are now good to go
* The main loop exits (the bot has shut down this plugin)
* stop() is called
* Your process is stopped (possibly by force)
 
Each line is processed by being passed to handle_line.
If an exception is raised during handle_line, the plugin name, and line that caused the exception are sent to #test. The stack trace is printed to stdout.

If using the default handle_line (that you got from importing plugin_base) then @command and @match hooks are evaluated at this time.

### Plugin Base
yakr.plugin_base provides a framework for plugins to use to interact with yakr. 
While not strictly necessary, it does help make plugin development less repetitive.

plugin_base provides the following functions

    start()
    ready()
    stop()
    handle_line(line)
    
    process_commands(line)
    process_matches(line)
    
    set_out_queue(queue)
    get_out_queue()
    
    join(channel)
    say(channel, message)
    topic(channel, topic)
    think(line)

    receiveSelfOutput(bool)
    set_command_prefix(prefix)
    
    @command(regex)
    @match(regex)
    @privmsg

**start, ready, stop, handle_line(line)** are callbacks for yakrs as described above.

**process_commands(line), process_matches(line)** are used by the default handle_line to check and call the decorators provided by plugin_base

**set_out_queue(queue), get_out_queue()** set the message queue that acts as the communication between yakr and your plugin

**receiveSelfOutput(bool) set_command_prefix(prefix)** are two lower level features provided to a plugin for more control. 

If a plugin needs to use other plugins output, or more specifically, see what yakr is putting into the network, a call to **receiveSelfOutput(True)** will enable that. This call should be made inside of ready() as calling it before then will break as yakr isn't ready to start receiving messages from plugins yet. 

By default commands are triggered with "!", if your plugin should use a different command prefix, then using this function will change what prefix the decorators use during building. This call should be made before any decorators are applied to functions inside your plugin. 

### plugin_base (continued) -- Decorators
** @command(regex) @match(regex) @privmsg** are convenience decorators to allow more rapid and pain free plugin development. These are your main hooks into the yakr system.

    from yakr.plugin_base import *
    @command("foo")
    def command_example(who, what, where):
        pass
    @match("(.*)")
    def match_example(groups):
        pass
    @privmsg
    def privmsg_example(who, what, where):
        pass

In the above examples:

* Who - the sender of the message
* What - the actual message or command
    * when commands are fired, this does not command the command or the prefix, only the argument passed to the command
* Where - the channel 
    * in the case of a private message, this is the sender too
    * where is usually where you should respond to.
* groups - the tuple of the captured data (regex.match(..).groups())

@command and @privmsg are processed via process_commands(line). 

@match is processed during process_matches(line)


### TODO
Stuff available to plugins
* [ ] Shelve
    * string->object persistant storage
* [ ] Log file
    * Logging object for your plugin 
* [ ] Config file
    * Basic config file parser (ConfigParser)
* [ ] Scheduling functions
    * After(timeout, callback) => eventId
    * Every(timeout, callback) => eventId
    * Cancel(eventId)

