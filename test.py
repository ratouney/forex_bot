import fxcmpy
import pandas as pd
import datetime as dt

def run(con):
    tr = con.open_trade(symbol="GBP/JPY", is_buy=True, amount=1, time_in_force='GTC', order_type='AtMarket', is_in_pips=False, stop=137.605, trailing_step=12)
    con.change_trade_stop_limit(trade_id=tr['tradeId'], is_stop=True, trailing_step=8)