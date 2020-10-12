from Session import Session
from ichimoku import *
import time
from datetime import datetime

s = Session("3d2c1e7fccc4e7dbe5cee89c58f6b34a2ba9743a")

instrument_list = None
if s.isConnected():
    instrument_list = s.getConnection().get_instruments()
    print("Instrument_List : ", instrument_list)

con = s.getConnection()

print("All setup, going !")
active = True
while active:
    run(con)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    time.sleep(90)
