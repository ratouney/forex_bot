import fxcmpy
import pandas as pd
import datetime as dt
from pylab import plt
from pyti.ichimoku_cloud import *
import mplfinance as mpf
from magic import *
plt.style.use('seaborn')

def run(con):
    currencies = ["XAU/USD", "GBP/JPY", "XAG/USD", "GER30", "USD/CNH", "EUR/JPY", "USD/JPY", "USD/CHF", "AUD/USD", "EUR/GBP", "NZD/USD", "USD/CAD", "CHF/JPY"] 
    cur = "GER30"
    period = "m1"
    blocks = 52

    # data, raw = readIchimoku(con, cur, period, blocks)
    # print(con.get_candles(cur, period=period, number=blocks))
    # print(raw)
    rt = con.open_trade(symbol="USD/CAD", time_in_force="GTC", order_type="AtMarket", is_buy=True, amount=1, is_in_pips=True, stop=-20, trailing_step=1)
    print(rt)