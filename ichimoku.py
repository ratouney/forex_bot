import fxcmpy
import pandas as pd
import datetime as dt

defaultArgs = {
    'high': "High",
    'low': "Low",
    'open': "Open",
    'close': "Close",
    'tkp': 9,
    'kjp': 26,
    'skbp': 52,
    'decimalpip': 2,
}

#   To get an accurate reading on all the lines,
#   you need the candles lenght to be TWICE the SenkouB period.
# 
#   With the default 52 period, you thus need 104 candles ! 
def addToCandles(currency, candles, **kwargs):
    args = defaultArgs
    args.update(kwargs)

    print("Cheking for JPY in ", currency)
    if "JPY" in currency:
        print("FOUND JPY")
        args['decimalpip'] = 3

    print("Decimal pips : ", args['decimalpip'])
    # Adding the TenkanSen
    tenkan_max = candles['High'].rolling(window = args['tkp'], min_periods = 0).max()
    tenkan_min = candles['Low'].rolling(window = args['tkp'], min_periods = 0).min()
    candles['tenkan_sen'] = round((tenkan_max + tenkan_min) / 2, args['decimalpip'])

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = candles['High'].rolling(window= args['kjp'], min_periods = 0).max()
    period26_low = candles['Low'].rolling(window= args['kjp'], min_periods = 0).min()
    candles['kijun_sen'] = round((period26_high + period26_low) / 2, args['decimalpip'])

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    candles['senkou_span_a'] = round(((candles['tenkan_sen'] + candles['kijun_sen']) / 2), args['decimalpip']).shift(args['kjp'])

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = candles['High'].rolling(window= args['skbp'], min_periods = 0).max()
    period52_low = candles['Low'].rolling(window= args['skbp'], min_periods = 0).min()
    candles['senkou_span_b'] = round(((period52_high + period52_low) / 2), args['decimalpip']).shift(args['kjp'])

    # The most current closing price plotted 26 time periods behind (optional)
    candles['chikou_span'] = candles['Close'].shift(-args['kjp'])

def analyse(currency, candles):
    decimalpip = 2

    if "JPY" in currency:
        decimalpip = 3

    blocks = len(candles)

    # Checking what signal the cloud calls for
    cloudColor = None
    if candles['senkou_span_a'][blocks - 1] > candles['senkou_span_b'][blocks - 1]:
        cloudColor = "Green"
    else:
        cloudColor = "Red"

    # Trying to see what the general trend indicates
    trend = None
    if candles['tenkan_sen'][blocks - 1] > candles['kijun_sen'][blocks - 1]:
        trend = "Up"
    else:
        trend = "Down"

    # Are we on a turning point
    turningPoint = None
    ctick = abs(candles['tenkan_sen'][blocks - 1] - candles['kijun_sen'][blocks - 1])
    print(ctick)

    



def run(con):
    currency = "XAU/USD"
    cand = con.get_candles(currency, period="m1", number=104, columns=['bids'])
    cand.columns = ['Open', 'Close', 'High', 'Low']
    addToCandles(currency, cand)
    analyse(cand)

    print(cand)