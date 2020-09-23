import importlib
from Session import Session
from Loader import Loader

s = Session("yourTOKEN")

instrument_list = None
if s.isConnected():
    instrument_list = s.getConnection().get_instruments()
    print("Instrument_List : ", instrument_list)

active = True
l = Loader()

while active:
    try:
        i = input("Enter module name : ")
        l.run(s, i)
    except KeyboardInterrupt:
        print("Closing connection")
        s.close()
        active = False
        continue

