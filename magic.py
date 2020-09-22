import fxcmpy
import pandas as pd
import datetime as dt

def run(con):
    print("Current account :", con.get_instruments_for_candles())