import importlib

class Loader():
    def __init__(self, file = None):
        self.__file__ = file

    def __currentFile__(self):
        return self.__file__
        
    def __load__(self, givenFile = None):
        if givenFile != None:
            self.__file__ = givenFile
        if givenFile == None and self.__file__ == None:
            raise Exception("No file name given")
        try:
            self.__mod__ = __import__(self.__file__)
        except Exception as e:
            print("Fuck : ", e)

    def run(self, session, modname, func = "run"):
        self.__load__(modname)
        try:
            getattr(self.__mod__, func)(session.getConnection())
        except Exception as e:
            print("Could not run function : ", e)

