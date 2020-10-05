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
    print(f'Loading {currency} : ', end="")
    if "JPY" in currency:
        pipDiff = 0.01
    else:
        pipDiff = 0.00001

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

    closeSignal = False
    openSignal = False

    # print("Currency : ", currency)
    # print(cand.iloc[blocks - 1:])

    if cand['senkou_span_a'][blocks - 1] > cand['senkou_span_b'][blocks - 1]:
        cloudColor = "Green"
    else:
        cloudColor = "Red"

    # print("Trend : ", currency)
    # print(cand.iloc[blocks - 2:])
    # print("LastTenkan : ", cand['tenkan_sen'][blocks - 1])
    # print("LastKiJun : ", cand['kijun_sen'][blocks - 1]) 
    if cand['tenkan_sen'][blocks - 1] > cand['kijun_sen'][blocks - 1]:
        trend = "Up"
    else:
        trend = "Down"

    if abs(cand['tenkan_sen'][blocks - 2] - cand['kijun_sen'][blocks - 2]) <= pipDiff:
        turningPoint = True

    median = (cand['Open'][blocks - 1] + cand['Close'][blocks - 1] + cand['High'][blocks - 1] + cand['Low'][blocks - 1]) / 4

    if cand['chikou_span'][blocks - 27] >= cand['Low'][blocks - 27] and cand['chikou_span'][blocks - 27] <= cand['High'][blocks - 27]:
        closeSignal = True


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

    if turningPoint and decision != None:
        openSignal = True

    print("Done")
    return {
        'Currency': currency,
        'Trend': trend,
        'CloudColor': cloudColor,
        'PositionToCloud': positionToCloud,
        'TurningPoint': turningPoint,
        'PossibleTrade': decision,
        'OpenSignal': openSignal,
        'CloseSignal': closeSignal,
        'LimitA': cand['senkou_span_a'][blocks - 1],
        'LimitB': cand['senkou_span_b'][blocks - 1],
    }

def run(con):
    # ins = con.get_instruments_for_candles()
    # print(ins)
    # return
    currencies = ["EUR/GBP"]
    # currencies = ["EUR/USD", "XAU/USD", "GBP/JPY", "GBP/USD", "XAG/USD", "GER30", "USD/CNH", "EUR/JPY", "USD/JPY", "CHF/JPY", "USD/CHF", "AUD/USD", "EUR/GBP", "NZD/USD", "USD/CAD"] 
    # currencies = ["XAU/USD", "GBP/JPY", "XAG/USD", "GER30", "USD/CNH", "EUR/JPY", "USD/JPY", "USD/CHF", "AUD/USD", "EUR/GBP", "NZD/USD", "USD/CAD", "CHF/JPY"] 
    period = "m1"
    blocks = 52
    title = f'{blocks} ticks of {period}'

    allCurrencies = pd.DataFrame([], columns=['Currency', 'Trend', 'CloudColor', 'PositionToCloud', 'TurningPoint', 'PossibleTrade', 'OpenSignal', 'CloseSignal', 'LimitA', 'LimitB'])
    for cur in currencies:
        allCurrencies = allCurrencies.append([readIchimoku(con, cur, period, blocks)])
    allCurrencies = allCurrencies.sort_values(by=['PossibleTrade'])

    orders = con.get_open_positions().T

    # Force it, just to test
    # allCurrencies.iloc[0]['OpenSignal'] = True

    print(allCurrencies)

    for idx, row in allCurrencies.iterrows():
        if row['OpenSignal'] == True and row['CloseSignal'] == True:
            continue
        if row['OpenSignal'] == True:
            print("Try to open a position on  : ", row['Currency'])

            # Check if you already have an open position
            found = False
            for o in orders:
                if orders[o]['currency'] == row['Currency']:
                    print("Found : ", orders[o])
                    found = True

            if found == False:
                # buy or sell ?
                isBuy = row['PossibleTrade'] == "Buy"
                print("Buy stuff")
                # con.open_trade(symbol=row['Currency'], is_buy=isBuy, amount="1", time_in_force='GTC', order_type='AtMarket')
        if row['CloseSignal'] == True:
            print("Try to close a position on  : ", row['Currency'])

            # Check if you already have an open position
            found = []
            for o in orders:
                if orders[o]['currency'] == row['Currency']:
                    print("Found : ", orders[o])
                    found.append(orders[o])

            if len(found) > 0:
                print("Sell these !")
                for f in found:
                    print("Closing : ", f)
                    con.close_trade(trade_id=f['tradeId'], amount=f['amountK'])
            
    # How to access a specific line
    # print(allCurrencies[allCurrencies['Currency'].str.match('EUR/USD')])

    # Plot a candle data thing, dont do it with the ichimoku stuff
    # mpf.plot(cand, **plotargs, title=title, addplot=toadd)