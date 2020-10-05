from Session import Session
from magic import *
import time

s = Session("cffb2229e78fc7db07867b22177fc96907476860")

instrument_list = None
if s.isConnected():
    instrument_list = s.getConnection().get_instruments()
    print("Instrument_List : ", instrument_list)

con = s.getConnection()

print("All setup, going !")
active = True
while active:
    run(con)
    time.sleep(10)
