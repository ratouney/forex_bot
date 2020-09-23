from importlib import reload

class Loader():
    def __init__(self, file = None):
        self.__file__ = file
        if file != None:
            self.__mod__ = __import__(file)

    def __currentFile__(self):
        return self.__file__
        
    def __load__(self, givenFile = None):
        if givenFile != None:
            self.__file__ = givenFile
        if givenFile == None and self.__file__ == None:
            raise Exception("No file name given")
        try:
            if givenFile == None:
                print("Reloading module")
                self.__mod__ = reload(self.__file__)
            else:
                print("Loading new one")
                self.__file__ = givenFile
                self.__mod__ = __import__(givenFile)
        except Exception as e:
            print("Fuck : ", e)

    def load(self, givenFile = None):
        return None

    def run(self, session, modname = None, func = "run"):
        if modname == None and self.__file__ == None:
            raise Exception("No module to be loaded")
        if modname == None:
            self.__mod__ = reload(self.__mod__)
        if modname != None:
            self.__file__ = modname
            self.__mod__ = __import__(modname)
        try:
            getattr(self.__mod__, func)(session.getConnection())
        except Exception as e:
            print("Could not run function : ", e)

