import importlib
from Session import Session
from testing import *
import time
from datetime import datetime, timedelta

# Main Acc  === 3d2c1e7fccc4e7dbe5cee89c58f6b34a2ba9743a
# Bot Run   === 43038ce05fe884fbc730cfc2835abc8e68d799fe
# 

s = Session("1aabfdfa4043e045114c5f5dcfdc622427657630")


current_time = np.array([datetime(2020, 11, 4), datetime(2020, 11, 3, 16, 20)])

print("Starting the simulation at : ", current_time[1])

print("Starting the simulation at : ", current_time[0])

interval = {'minutes': 1}

instrument_list = None
if s.isConnected():
    instrument_list = s.getConnection().get_instruments()
    print("Instrument_List : ", instrument_list)

con = s.getConnection()

print("All setup, running simulation !")
currencies = ["GBP/JPY", "GBP/USD", "USD/CNH", "EUR/JPY", "USD/JPY", "CHF/JPY", "USD/CHF", "EUR/GBP", "NZD/USD", "USD/CAD", "AUD/JPY", "AUD/USD", "EUR/CHF", "GBP/CHF", "EUR/AUD", "EUR/CAD"]
close = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
orderType = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
status = np.array([currencies, close, orderType])

currently = current_time[1]
while currently != current_time[0]:
    print("Currently : ", current_time[1])
    current_time[0] = current_time[0] + timedelta(**interval)
    current_time[1] = current_time[1] + timedelta(**interval)
    status = run(con, current_time, status)
    time.sleep(1)