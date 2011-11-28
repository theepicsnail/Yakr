import sys
import os
from Logger import logger
class PluginManager:
    loaded = {}
    path = ""
    def __init__(self,path):
        self.path = path
        logger.info("Plugin manager created. <{}>".format(path))
        sys.path.append(path)

    def load(self,name):
        logger.debug("Loading <{}>".format(name))
        try:
            self.loaded[name]=__import__(name)
        except:
            logger.exception("Failed to load <{}>".format(name))
    def unload(self,name):
        logger.debug("Unloading <{}>".format(name))
        if name in self.loaded.keys():
            mod = self.loaded[name]
            del self.loaded[name]
            del sys.modules[name]     
            try:
                os.remove(mod.__file__+"c")#try to remove the .pyc
            except:pass

    def plugins(self):
        return self.loaded.items()                

    def autoload(self):
        for pname in filter(lambda x:x.endswith(".py"),
                            list(os.walk(self.path))[0][2]):
            try:
                self.load(pname[:-3])
            except:
                pass 
