import importlib
from Session import Session
from Loader import Loader

s = Session("cffb2229e78fc7db07867b22177fc96907476860")

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

