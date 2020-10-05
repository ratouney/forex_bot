import importlib
from Session import Session
from Loader import Loader

s = Session("3d2c1e7fccc4e7dbe5cee89c58f6b34a2ba9743a")

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


