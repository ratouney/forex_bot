print("Loading the lib")
import fxcmpy
print("Lib is loaded")

import logging

lg = logging.getLogger("FXCM")
print(lg)

class Session():
    def __init__(self, token):
        self.__token__ = token
        self.__connection__ = None

        print("Starting connection")
        try:
            self.__connection__ = fxcmpy.fxcmpy(access_token=token, log_file="log.txt", server="demo")
            print("Connection successfull")
        except Exception as e:
            self.__connection__ = None
            print("Connection failed : ", e)

    def close(self):
        if self.__connection__ != None:
            print("Connection closed")
            self.__connection__.close()

    def isConnected(self):
        if self.__connection__ == None:
            return False
        return self.__connection__.is_connected()

    def getConnection(self):
        if self.isConnected():
            return self.__connection__