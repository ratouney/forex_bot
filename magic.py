import fxcmpy
import pandas as pd
import datetime as dt

def run(con):
    cand = con.get_candles("XAU/USD", period="M1", number=5)
    print("fok")
    print(cand)