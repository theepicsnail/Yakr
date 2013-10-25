import os.path

def plugin_exists(plugin_name):
    return os.path.isfile("plugins/{}.py".format(plugin_name))

def get_plugin_name():
    """Gets a plugin name from the user.
    Returns the name if it's valid.
    Returns "" if the user wants to quit.
    """

    raw_input("""
    This will walk you though creating a new plugin. Press enter to continue
    """)

    plugin_name = raw_input("""
    Enter a plugin name. Plugin names are all lower case, and do not start with numbers.
    Generally you'll want to name your plugin something similar to its main feature.
    !tell is named 'tell' 
    !s is named 'sed'
    !alarm is named 'alarm'
    Name:""")

    while plugin_name != "" and plugin_exists(plugin_name):
        plugin_name = raw_input("""
        A plugin with that name already exists. Try naming it something else.
        Or just press enter to quit.
        New Name:""")

    return plugin_name 

def configure_more():
    more = raw_input("""
    Would you like to configure the plugin more before it gets created?
    Configuring more will write some of the boiler plate for you. 
    If you choose not to configure more, you will get a template plugin
    with a lot of unnecessary code.
    Configure more y/[n] """)

    while more not in ["", "y", "n"]:
        more = raw_input("""
        Please use 'y' to indicate you would like to configure more.
        Please use 'n' or just press enter to indicate you would not.
        Configure more y/[n] """)

    return more == "y" 

def explain_configure_more():
    raw_input("""
    Extended configuration:

    Configuration is broken into 3 parts.
    1) Configuring the states (plugin loaded, ready, stopping)
    2) Configuring the hooks (when should your plugin react)
    3) Configuring the utilities (what other methods will you need)
    Press enter to begin 
    """)

def get_block_input(prompt):
    data = raw_input(prompt + """
    You can use multiple lines, use an empty line to finish typing
""")
    just_input = data
    while just_input != "":
        just_input = raw_input()
        if just_input != "":
            data += "\n" + just_input
    return data

def configure_states():
    code = ""
    print """
    +------
    | Configure states|
                ------+
    There are 3 states to optionally configure:
    start - when the plugin is just loaded
    ready - when the plugin is able to send messages/join channels/etc..
    stop - when the plugin should shut down.
    We'll configure each of these now:
    """

    
    about_start = get_block_input("""
    start()
    What should your plugin do when it is first loaded.
    This is before your plugin is able to join/send messages, etc..
    E.g. 'connect to the db and open foo.txt'
    If you do not need a start() method, just press enter.
    """)
    if about_start != "":
        code += """
def start():
    \"\"\"{}\"\"\"
    pass
""".format(about_start)

    about_ready = get_block_input("""
    ready()
    Now your plugin is ready to start doing stuff.
    What should its first actions be? 
    E.g. 'join #foo and set the topic to "hello world"'
    If you do not need a ready() method, just press enter.
    """)
    if about_ready != "":
        code += """
def ready():
    \"\"\"{}\"\"\"
    pass
""".format(about_ready)

    about_stop = get_block_input("""
    stop()
    Now your plugin is shutting down, what does it need to take care of here?
    Actions performed here may not work, so do not rely on them. 
    E.g. 'disconnect from the db and save the cache to a file'
    """)
    if about_stop != "":
        code += """
def stop():
    \"\"\"{}\"\"\"
    pass
""".format(about_stop)

    return code

def hook_input(hook_phrase):
    block_quote = "\n    \"\"\"{}\"\"\""
    entered = []
    entered_name = raw_input("""
    Enter a {}.
    or press enter to finish.
    """.format(hook_phrase))
    while entered_name != "":
        entered_comment = get_block_input("""
    What should happen when this is triggered?""")
        if entered_comment:
            entered_comment = block_quote.format(entered_comment)
        entered.append((entered_name, entered_comment))
        
        entered_name = raw_input("""
    Enter another {}
    or press enter to continue:
    """.format(hook_phrase))

    return entered


def configure_hooks():
    print """
    +------
    | Configure Hooks|
               ------+
    We'll now configure any hooks for your plugin.
    Hooks are callbacks that are fired when certain irc lines are seen by your plugin.
    There are 3 kinds:
    command - Triggered by a user explicitly (e.g !tell is the command 'tell')
        These are what you should use for passive features (ones that need a user to trigger it)
    privmsg - When a message is seen by the bot in either a channel or a private message
        These are what you should use for active features (ones that react to messages without explicit triggering)
    regex - Triggered when an irc line matches a particular regular expression
        These are if what you should use if you need non message hooks (notice/topics/etc..)
    """
    
    code = ""

    commands = hook_input("command (without the !)")
    for name, comment in commands:
        code += """
@command("{}")
def {}():{}
    pass
""".format(name,name,comment)

    privmsgs = hook_input("privmsg handler")
    for name, comment in privmsgs:
        code += """
@privmsg
def {}():{}
    pass
""".format(name, comment)

    matches = hook_input("regex handler")
    for name, comment in matches:
        code += """
@match("YOUR REGEX HERE")
def {}():{}
    pass
""".format(name, comment)

    return code

def configure_utils():
    print """
    +------
    | Configure Utility functions|
                           ------+
    Last but not least, if you have some functions that 
    your plugin will need to do, you can set them up here.
    E.g: schedule_alarm, connect_to_db, etc..
    """
    
    utils = hook_input("utility function's name")
    code = ""
    for name, comment in utils:
        code += """
def {}():{}
    pass
""".format(name, comment)

    return code

def interactive():
    plugin_name = get_plugin_name()
    if plugin_name == "":
        return

    plugin_code = ""

    if configure_more():
        plugin_code = "from yakr.plugin_base import *\n"
        explain_configure_more()
        print "\n" * 10
        plugin_code += configure_states()
        print "\n" * 10
        plugin_code += configure_hooks()
        print "\n" * 10
        plugin_code += configure_utils()
    else:
        plugin_code = file("yakr/plugin_template.py").read()
    print "\n" * 10
    print "---", plugin_name, "---"
    print plugin_code
    print "Save this as ",plugin_name+".py?"
    if raw_input("y/[n] ")=="y":
        file("plugins/{}.py".format(plugin_name), "w").write(plugin_code)

if __name__=="__main__":
    interactive()

