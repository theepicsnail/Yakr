Yakr is yet another IRC bot. This one is designed to be very thin, with the same plugability of Superbot and Superbot2.

### Starting

To **start** the bot:
(Be sure to configure the bot first!)

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
 


### Plugin Base

yakr.plugin_base provides a framework for plugins to use to interact with yakr. 
While not strictly necessary, it does help make plugin development less repetitive.




To start a new plugin:
python Main.py makePlugin <pluginName>
  this will create
  plugins/<pluginName>/__init__.py
    Empty, this needs to be present for the plugin to be loadable
  plugins/<pluginName>/<pluginName>.py
    Template plugin

To debug your plugins:
During the process of working on a plugin, it's useful to test a feature many times during development. To aid that record/replay exist.
plugin Main.py record
  this will start the bot in "record" mode.
  Do this, then try out your plugin, once done, kill this process (ctrl-c)
  This will create a (or overwrite the) RECORD file.
  Once recorded, you will be able to replay (see next section)

To reply the recorded data
plugin Main.py replay
  this will start up a fake bot that doesn't connect to a server (keeps you from spamming, or needing to load/reload plugins)
  the RECORD file will be played through the bot to simulate the network data it experienced during the recording.
  The actions/outputs/etc.. from the plugins will be recorded into log files so that you can inspect what has happened.
  using pdb during your plugin is safe as well, since replay mode doesn't connect to a server, you can't ping out.
  replay can be done repeatedly until your plugin is working in replay mode

To test your plugin:
python Main.py test 
  Same as below, except tests all loadable plugins
python Main.py test <pluginName>
  if plugins/<pluginName>/<pluginName>Test.py exists, it is executed.


-------
plugins
-------
Plugins shouldn't have any global code

Life of a plugin:
  Plugin is imported
    Global code runs here, you shouldn't have any global code.

  onStart() called
    plugin is now created, it'll be receiving events and what not after this
    This happens possibly even before the irc connection has been made, or hand shakes, etc..

  onReady() called
    Ready is probably where you'll want to do your actual bot stuff upon loading. Ready is called once
    the connection is now ready for you to send commands (joins, messages, etc..)

  Right here is where the plugin will spend most of its life, making calls to your callbacks and what not.

  onStop() called 
    before shutdown 
    and when the plugin is being unloaded

  This is the reccomended way to trigger an event in your plugin: it will allow for future events to work, and
  it ensures a more consistant functionality across plugins. This should also allow name collision resolution
  !plugin1.foo
  !plugin2.foo

  @command("foo")
  def onCall(*args, *kwargs):
    args will consist of the "tokenized" chunks of strings
    for example:
    !foo bar baz
      would come across as onCall(["bar", "baz"]) 
    !foo "bar baz"
      would come across as onCall(["bar baz"])
    repeat 'test' | foo 
      would come across as onCall(["test"])
    $(repeat foo bar)
      would come across as onCall(["bar"])
      This is because $( ) takes the output of whatever command is in it and reprocesses is
      so repeat foo bar outputs "foo bar"
      which gets reprocessed and "bar" becomes the argument

    kwargs remains unused at the moment, something like
    "foo bar=baz" for now will just be processed as onCall(["bar=baz"])

  Just returning a string, will attempt to go back to wherever is most approriate
    If a message came from a channel, it'll be sent back to the channel
    If a message came from a private message, it'll be sent back to the sender
    If a message came from a notice, it'll be noticed back at the sender (this is against the IRC RFC, oops)
  If you're sending a message from where that the proper recipient can't be determined (eg, some timer based event) then 
    a warning is logged, and the message is discarded.

Message format:
The same coloring syntax is used as before (extended!):
    {f} sets the fg color to color f
    {f,} same as above
    {,b} sets the background color to b
    {f,b} sets foreground to f, background to b
    {,,b} sets bold
    {,,i} sets italic
    {,,u} sets underline
    so, {1,2,biu} would result in foreground = 1, background = 2, bold, italic, and underline
    {} resets all attributes

  If a line starts with @ this will specify where to sent the message
    @nick
    @#channel

  If a message starts with * and ends with *, (after the optional @ director)
    then the message will be sent as an action.
  
  @snail *{1}pokes*
    will send a private message as an action, in the foreground color 1
  
  If a message contains a newline, this creates a new message entirely, everything is reset (lines are handled disjointly)
    so the string
      "@snail *poke*\nHello there."
    will be parsed as:
      "@snail *poke*"
      "Hello there"
    so "Hello there" may end up not going to snail. 
      e.g. if this is in response to an action in #adullm, "hello there" will goto adullam

  Any blank lines are ignored.
    the string
      "@snail hello\n\n\nworld"
      will be parsed as:
      "@snail hello"
      ""
      ""
      "world"
    which then gets filtered down to
      "@snail hello"
      "world"  <- remember this line may not go to snail

  Protip:
    "\n@snail ".join(["", "hello", "*poke*"])
    produces:
      "\n@snail hello\n@snail *poke*"
    which gets parsed as:
      ""
      "@snail hello"
      "@snail *poke*"
    which gets filtered to:
      "@snail hello"
      "@snail *poke*"
    This might be useful enough to warrent some helper/util method:
      def whatever(prefix, lines):
        return ("\n" + prefix + " ").join([""] + lines)


Methods like 
  tell("#adullam", "hello")
  action("#adullam", "hello")
  etc.. are just string modifiers:

  def tell(target, message):
    return "\n@" + target + " " + message

  def action(target, message):
    return "\n@" + target + " *" + message + "*"

  This allows for:
  out = tell("#adullam", "hi")
  out += action("snail", "poke")
  return out
    out = "\n@#adullam hi\n@snail *poke*"

  to actually push a message through the bot:
  send(formatted message)
    this is NOT recommended during the command function as only the returned message will be handled correctly (piped, reprocessed, etc..)
    if you're doing a send, you need to 




Stuff available to plugins
  [ ] Shelve
    string->object persistant storage
  [ ] Log file
    Logging object for your plugin 
  [ ] Config file
    Basic config file parser (ConfigParser)
  Bot (Yakr!)
    Message building
      Msg(target, message)
      Action(target, message)
        (should Action just do the *'s then used like Msg(target, Action("pokes")) ?)
        I don't know if Action really needs to know about where the action is going.
      Color(fg=None, bg=None, attrs=None)
    Actions
      Send(formattedMessage)
      Join(channel)
      Part(channel)
      etc..
    Scheduling functions
      After(timeout, callback) => eventId
      Every(timeout, callback) => eventId
      Cancel(eventId)

