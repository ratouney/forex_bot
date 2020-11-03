from Session import Session
from ichimoku import *
import time
from datetime import datetime, timedelta

# Main Acc  === 3d2c1e7fccc4e7dbe5cee89c58f6b34a2ba9743a
# Bot Run   === 43038ce05fe884fbc730cfc2835abc8e68d799fe
# 
runFrom = datetime(2020, 11, 1)
print("Starting the simulation at : ", runFrom)
runTo = datetime(2020, 11, 3)
print("Starting the simulation at : ", runTo)

interval = {'minutes': 5}

s = Session("43038ce05fe884fbc730cfc2835abc8e68d799fe")

instrument_list = None
if s.isConnected():
    instrument_list = s.getConnection().get_instruments()
    print("Instrument_List : ", instrument_list)

con = s.getConnection()

print("All setup, running simulation !")

currently = runFrom
while currently != runTo:
    print("Currently : ", currently)
    currently = currently + timedelta(**interval)
    run(con, currently)
    time.sleep(1)