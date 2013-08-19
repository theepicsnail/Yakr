""" 
Config file reading tool for Yakr and plugins.
"""

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

def read(config_file):
    """
    Read a config file, then create a dictionary from the contents.

    [section1]
    foo = bar
    [section2]
    foo = 1
    bar = 2

    turns into

    {"section1": {"foo": "bar"},
     "section2": {"foo":1, "bar":2}}
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    out = {}
    for section in config.sections():
        out[section] = dict(config.items(section))
    del config
    return out
