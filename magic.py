import fxcmpy
import pandas as pd
import datetime as dt
from pylab import plt
from pyti.ichimoku_cloud import *
import mplfinance as mpf
plt.style.use('seaborn')

plotargs = dict(
    type="candle",
    style="checkers",
    figscale=1.5,
    figratio=(15,9)
)

def addIchimoku(candles):
    # Adding the TenkanSen
    tenkan_max = candles['High'].rolling(window = 9, min_periods = 0).max()
    tenkan_min = candles['Low'].rolling(window = 9, min_periods = 0).min()
    candles['tenkan_sen'] = (tenkan_max + tenkan_min) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = candles['High'].rolling(window=26, min_periods = 0).max()
    period26_low = candles['Low'].rolling(window=26, min_periods = 0).min()
    candles['kijun_sen'] = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    candles['senkou_span_a'] = ((candles['tenkan_sen'] + candles['kijun_sen']) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = candles['High'].rolling(window=52, min_periods = 0).max()
    period52_low = candles['Low'].rolling(window=52, min_periods = 0).min()
    candles['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)

    # The most current closing price plotted 26 time periods behind (optional)
    candles['chikou_span'] = candles['Close'].shift(-26)

    return candles

def readIchimoku(con, currency, period="m5", blocks=52):
    if "JPY" in currency:
        pipDiff = 0.01
    else:
        pipDiff = 0.0001

    cand = con.get_candles(currency, period=period, number=blocks, columns=['bids'])
    cand.columns = ['Open', 'Close', 'High', 'Low']
    cand = addIchimoku(cand)

    # This is for plotting
    # toadd = [
        # mpf.make_addplot(cand['tenkan_sen']),
        # mpf.make_addplot(cand['kijun_sen']),
    # ]

    cloudColor = None
    positionToCloud = None
    trend = None
    turningPoint = False

    # print("Currency : ", currency)
    # print(cand.iloc[blocks - 1:])

    if cand['senkou_span_a'][blocks - 1] < cand['senkou_span_b'][blocks - 1]:
        cloudColor = "Green"
    else:
        cloudColor = "Red"
    if cand['tenkan_sen'][blocks - 1] > cand['kijun_sen'][blocks - 1]:
        trend = "Up"
    else:
        trend = "Down"
    if abs(cand['tenkan_sen'][blocks - 2] - cand['kijun_sen'][blocks - 2]) <= pipDiff:
        turningPoint = True

    median = (cand['Open'][blocks - 1] + cand['Close'][blocks - 1] + cand['High'][blocks - 1] + cand['Low'][blocks - 1]) / 4

    if abs(cand['senkou_span_a'][blocks - 1] - cand['senkou_span_b'][blocks - 1]) <= pipDiff:
        cloudColor = "Black"
        positionToCloud = "Irrelevant"
    elif median > cand['senkou_span_a'][blocks - 1] and median > cand['senkou_span_b'][blocks - 1]:
        positionToCloud = "Above"
    elif median < cand['senkou_span_a'][blocks - 1] and median < cand['senkou_span_b'][blocks - 1]:
        positionToCloud = "Under"
    else:
        positionToCloud = "Inside"

    decision = None
    if positionToCloud == "Above" and trend == "Up" and cloudColor == "Green":
        decision = "Buy"
    if positionToCloud == "Under" and trend == "Down" and cloudColor == "Red":
        decision = "Sell"

    return {
        'Currency': currency,
        'Trend': trend,
        'CloudColor': cloudColor,
        'PositionToCloud': positionToCloud,
        'TurningPoint': turningPoint,
        'PossibleTrade': decision
    }

def run(con):
    # ins = con.get_instruments_for_candles()
    # print(ins)
    # return
    currencies = ["EUR/USD", "GBP/JPY", "USD/JPY", "XAU/USD", "GBP/USD", "XAG/USD", "EUR/JPY", "CHF/JPY", "XAG/USD", "UK100", "GER30"] 
    period = "h1"
    blocks = 52
    # title = f'{currency} - {blocks} ticks of {period}'

    allCurrencies = pd.DataFrame([], columns=['Currency', 'Trend', 'CloudColor', 'PositionToCloud', 'TurningPoint', 'PossibleTrade'])
    for cur in currencies:
        allCurrencies = allCurrencies.append([readIchimoku(con, cur)])
    print(allCurrencies)
    # How to access a specific line
    # print(allCurrencies[allCurrencies['Currency'].str.match('EUR/USD')])

    # Plot a candle data thing, dont do it with the ichimoku stuff
    # mpf.plot(cand, **plotargs, title=title, addplot=toadd)