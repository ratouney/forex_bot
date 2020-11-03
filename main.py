import importlib

from Session import Session
from Loader import Loader

s = Session("43038ce05fe884fbc730cfc2835abc8e68d799fe")

instrument_list = None
if s.isConnected():
    instrument_list = s.getConnection().get_instruments()
    print("Instrument_List : ", instrument_list)

active = True
l = Loader()

prev = None
while active:
    try:
        i = input("Enter module name : ")
        print("Got [", i, "]")
        if prev == None or prev != i and i != "":
            prev = i
            l.run(s, i)
        else:
            l.run(s)

    except KeyboardInterrupt:
        print("Closing connection")
        s.close()
        active = False
        continue
    except Exception as e:
        print("Fail : ", e)
        continue


