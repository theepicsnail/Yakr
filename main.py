""" 
    main.py -- main entry point for yakr
    this doc string should be more helpful
"""
import argparse
import yakr.config
import yakr.plugin_manager
import yakr.networking
import yakr.connection
import yakr.bot
#import yakr.plugin_manager
#import yakr.networking
#def load_plugins(bot):
#    """
#    Scan for, and import all available plugins
#    """
#    logger.info("Starting plugin scan")
#    for plugin in [ x for x in os.listdir('plugins') if "_" not in x ]:
#        logger.info(plugin)
#        module = __import__("plugins.%s" % plugin, {}, {}, [plugin])
#        logger.info(module)

_YAKR_DOC_ = """Yakr
---------------
github.com/theepicsnail/Yakr

blah
blah blah
"""
def main():
    """ main """
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=_YAKR_DOC_)

    parser.add_argument("-c", "--config",
            metavar="config",
            help="specify a config file (default: yakr.cfg)",
            default="yakr.cfg")

    parser.add_argument("action", 
            choices=["run", "make_plugin", "record", "replay", "test"],
            help="action to run",
            default=0)

    parser.add_argument("plugins", 
            metavar="plugin", 
            nargs="*",
            help="which plugins to use (default: all available)",
            default=[None])

    args = parser.parse_args()
    config = yakr.config.read(args.config)
    plugins = args.plugins
    if plugins[0] is None:
        plugins = yakr.plugin_manager.discover_plugins(config["plugin"]["path"])
    globals()[args.action](config, plugins)

def run(config, plugins):
    """
    Run the bot loading the specified plugins
    if plugins is None, load all plugins possible 
    """
    bot = yakr.bot.Bot()
    bot.load_config(config)
    for plugin in plugins:
        bot.load_plugin(plugin)
    bot.run()

def make_plugin(config, plugins):
    raise Exception("Not implemented")

def record(config, plugins):
    raise Exception("Not implemented")

def replay(config, plugins):
    raise Exception("Not implemented")

def test(config, plugins):
    raise Exception("Not implemented")

     
if __name__ == '__main__':
    main()

    #Create the plugin manager
    #Create the connection
    #irc_bot = Irc.RealBot(SETTINGS)
    #Bot.setPluginHandler(irc_bot) 
    #irc_bot.start()
    #irc_bot.wait()
