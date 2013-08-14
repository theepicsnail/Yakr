"""
    This handles yakrs connection settings and utility methods.
    When the bot is running in 
        run
            this will use the config file to determine the proper tcp handler.
            as well as the connection details.
        record
            this will work the same as 'run' but with an added recording layer
            to record all in bound traffic, to be played back throug "replay"
        replay
            this will check for a RECORD file and use that as the network 
            connecton any output messages will be logged as well for debugging.
        test/make_plugin
            these modes do not utilize the connection module

    The connection interface requires that anything being set as the connection
    provides the following:
        get_input() returns an object with .get() returns string
        get_output() returns an object with .put(string)
        connect() blocks while processing input and output
    the strings returned from .get and put into .put are expected to have no
    newline markers
"""

class Connection:
    def __init__(self, connection):
        """
        Set the connection used by yakr.
        connection should provide a get_input which returns something with a .get
        it should also provide get_output which has a .put(string)
        and lastly a connect method that blocks until the connection is closed
        """

        self.data_in = connection.get_input()
        self.data_out = connection.get_output()
        self.connectLoop = connection.connect

    def main_loop(self): 
        """
        Enter the connections main loop.
        The connection should (during its looping) put items into the 
        queue that was provided through get_input, and it should consume
        items that it gets through the queue provided by get_output
        """
        self.connectLoop()
