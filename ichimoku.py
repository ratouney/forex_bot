import fxcmpy
import ctypes
import pandas as pd
import datetime as dt
import mplfinance as mpf
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time

defaultArgs = {
    'high': "High",
    'low': "Low",
    'open': "Open",
    'close': "Close",
    'tkp': 15,
    'kjp': 52,
    'skbp': 104,
    'decimalpip': 5,
}

def indicDMI(periodN, periodV, currency, redline, con):
    periodN2 = int(periodN / 100)
    if (periodN2 < 10):
        periodN2 = 10
    if (periodN2 > 20):
        periodN2 = 20
    y = 0
    data = con.get_candles(currency, period=periodV, number=periodN2)
    dmi = dmicalculation(data, periodN2)
    for i in range (periodN2):
        if (dmi[1][i] == -21):
            print("can't buy (-21)")
            redline = False
    for i in range (periodN2):
        if (dmi[1][i] <= 0):
            y = y + 1
    if (y >= int(periodN2 - periodN2 / 3)):
        print("can't buy (7/10 < 0)")
        redline = False
    return redline

def indicRSI(periodN, periodV, currency, redline, con):
    result = {
        'redline': False,
        'type': None,
    }
    periodN2 = int(periodN / 100)
    if (periodN2 < 10):
        periodN2 = 10
    if (periodN2 > 20):
        periodN2 = 20
    y = 0
    z = 0
    data = con.get_candles(currency, period='H1', number=500)
    rsi = rsicalculation(data, periodN2)
    data = con.get_candles(currency, period=periodV, number=periodN2)
    dataY1 = data.loc[:, ['bidopen']].to_numpy()
    dataY2 = data.loc[:, ['bidclose']].to_numpy()
    dataY = (dataY1 + dataY2) / 2
    for i in range(periodN2):
        if (dataY[i] <= rsi[0][0]):
            y = y + 1
        if (dataY[i] >= rsi[1][0]):
            z = z + 1
    if (y >= int(periodN2 - periodN2 / 2.5)):
        # print("Warning : the market is in oversell, we should consider buying aiming long")
        redline = True
        result['redline'] = True
        result['type'] = 'short'
    if (z >= int(periodN2 - periodN2 / 2.5)):
        # print("Warning : the market is in overbought, we should consider selling aiming long")
        redline = True
        result['redline'] = True
        result['type'] = 'long'
    return result

def indicMVA(MVA1, MVA2, MVA3, periodN):
    redline = True
    indic = False
    for i in range (int(periodN / 100)):
        if (MVA2[0][MVA2[0].size - i - 1]) < (MVA3[0][MVA3[0].size - i - 1]):
            indic = True
            redline = False
    if (indic == True):
        # print("can't buy (MVA2 < MVA3)")
        indic = False
    for y in range (int(periodN / 100)):
        if (MVA1[0][MVA1[0].size - i - 1]) < (MVA2[0][MVA2[0].size - i - 1]):
            redline = False
            indic = True
    if (indic == True):
        # print("can't buy (MVA1 < MVA2)")
        indic = False
    return redline    


def dmicalculation(data, periodN):
    dataX = np.arange(periodN)
    dataY1 = data.loc[:, ['bidopen']].to_numpy()
    dataY2 = data.loc[:, ['bidclose']].to_numpy()
    dataY = (dataY1 + dataY2) / 2
    posdmi = np.array([0])
    negdmi = np.array([0])
    neg = 0
    pos = 0
    for i in range(periodN - 1):
        if (dataY[i] < dataY[i + 1]):
            pos = pos + 1
            posdmi = np.append(posdmi, posdmi[i] + pos)
            negdmi = np.append(negdmi, negdmi[i] + ((neg * neg + neg) / 2))
            neg = 0
        if (dataY[i] >= dataY[ i + 1]):
            neg = neg + 1
            posdmi = np.append(posdmi, posdmi[i] - ((pos * pos + pos) / 2))
            negdmi = np.append(negdmi, negdmi[i] - neg)
            pos = 0
    dmi = np.array([negdmi, posdmi])
    return dmi

def rsicalculation(data, periodN):

    dataX = np.arange(periodN)
    dataY1 = data.loc[:, ['bidopen']].to_numpy()
    dataY2 = data.loc[:, ['bidclose']].to_numpy()
    dataY = (dataY1 + dataY2) / 2

    sigma = np.nanstd(dataY)
    moy = np.nanmean(dataY)
    rsilow = np.full(periodN, moy - 1.6 * sigma)
    rsihigh = np.full(periodN, moy + 1.6 * sigma)
    rsi = np.array([rsilow, rsihigh])
    return rsi

def moving_average(a, n=4) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def createtendency(data, periods, periodN):    
    
    dataY1 = data.loc[:, ['bidopen']].to_numpy()
    dataY2 = data.loc[:, ['bidclose']].to_numpy()
    dataY = (dataY1 + dataY2) / 2
    
    MVAX = moving_average(dataY, n=periods)
    MVAY = np.arange(0, periodN - 1, (periodN / MVAX.size))
    movingaverage = np.array([MVAX, MVAY])

    return movingaverage

    
def resultbycurrency(con, currency, period, periodCount):

    periodN = periodCount
    data = con.get_candles(currency, period=period, number=periodN)

    MVA1 = createtendency(data, int(periodN / 20), periodN)
    MVA2 = createtendency(data, int(periodN / 10), periodN)
    MVA3 = createtendency(data, int(periodN / 5), periodN)
    rsi = rsicalculation(data, periodN)
    dmi = dmicalculation(data, periodN)
    result = {
        'tendencyValidation': False
    }
    redline = indicMVA(MVA1, MVA2, MVA3, periodN)
    result['MVA'] = redline
    redline = indicDMI(periodN, 'm15', currency, redline, con)
    result['DMI'] = redline
    if (redline == True):
        print("You can buy now on " + currency)
        result['tendencyValidation'] = True
        redline = False
    rsiOutput = indicRSI(periodN, 'm15', currency, redline, con)
    result.update(rsiOutput)
    return result 

#   To get an accurate reading on all the lines,
#   you need the candles lenght to be TWICE the SenkouB period.
# 
#   With the default 52 period, you thus need 104 candles ! 
def addToCandles(currency, candles, **kwargs):
    print("Loading ", currency)
    args = defaultArgs
    args.update(kwargs)

    if "JPY" in currency:
        args['decimalpip'] = 3
    else:
        args['decimalpip'] = 5

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

    return args

def analyse(currency, candles, args):
    decimalpip = args['decimalpip']

    blocks = len(candles)

    # Checking what signal the cloud calls for
    # Green means you should buy, red means selling
    cloudColor = None
    r1 = candles['senkou_span_a'][blocks - 1]
    r2 = candles['senkou_span_b'][blocks - 1]
    if r1 > r2:
        cloudColor = "Green"
    else:
        cloudColor = "Red"

    # If the prices are in the cloud, meaning trades are way more risky
    priceInCloud = False
    positionToCloud = "Inside"
    priceMarks = []
    start = candles['Low'][blocks - 1]
    end = candles['High'][blocks - 1]
    step = (end - start) / 10
    for i in range(0, 10):
        priceMarks.append(start + (step * i))
    above = 0
    inRange = 0
    under = 0
    for val in priceMarks:
        if r1 >= r2:
            if val <= r1 and val >= r2:
                inRange += 1
                continue
            if val > r1:
                above += 1
                continue
            if val < r2:
                under += 1
                continue
        else:
            if val <= r2 and val >= r1:
                inRange += 1
                continue
            if val < r1:
                under += 1
                continue
            if val > r2:
                above += 1
                continue
    if inRange >= 3:
        # This means 40% of the price bar is in the cloud
        priceInCloud = True
    if under >= 4:
        positionToCloud = "Under"
    if above >= 4:
        positionToCloud = "Above"

    # If it's too close to the cloud, just dont
    # print("B1Low [", candles['Low'][blocks - 1], "] - B1High [", candles['High'][blocks - 1], " == ", round(abs(candles['Low'][blocks - 1] - candles['High'][blocks - 1]), decimalpip))
    # print("B2Low [", candles['Low'][blocks - 2], "] - B2High [", candles['High'][blocks - 2], " == ", round(abs(candles['Low'][blocks - 2] - candles['High'][blocks - 2]), decimalpip))
    # print("B3Low [", candles['Low'][blocks - 3], "] - B3High [", candles['High'][blocks - 3], " == ", round(abs(candles['Low'][blocks - 3] - candles['High'][blocks - 3]), decimalpip))
    last3valAv = (abs(candles['Low'][blocks - 1] - candles['High'][blocks - 1]) +
                abs(candles['Low'][blocks - 2] - candles['High'][blocks - 2]) + 
                abs(candles['Low'][blocks - 3] - candles['High'][blocks - 3])) / 3
    # print("Average Diff : ", round(last3valAv, decimalpip))
    distance = 0
    if cloudColor == "Green":
        if positionToCloud == "Above":
            distance = candles['Low'][blocks - 1] - r1
        else:
            distance = r2 - candles['High'][blocks - 1]
    else:
        if positionToCloud == "Under":
            distance = r1 - candles['High'][blocks - 1]
        else:
            distance = candles['Low'][blocks - 1] - r2
    distance = abs(distance)
    closetoCloud = distance < last3valAv 


    # Trying to see what the general trend indicates
    # given the tenkan/kijun moving averages
    trend = None
    if candles['tenkan_sen'][blocks - 1] > candles['kijun_sen'][blocks - 1]:
        trend = "Up"
    else:
        trend = "Down"

    # Is there a recent turning point ?
    turningPoint = False
    ctick1 = abs(candles['tenkan_sen'][blocks - 1] - candles['kijun_sen'][blocks - 1])
    ctick2 = abs(candles['tenkan_sen'][blocks - 2] - candles['kijun_sen'][blocks - 2])
    ctick3 = abs(candles['tenkan_sen'][blocks - 3] - candles['kijun_sen'][blocks - 3])
    # ctick4 = abs(candles['tenkan_sen'][blocks - 4] - candles['kijun_sen'][blocks - 4])

    # Taking the pre-last candle, check if the difference between the Tenkan and Kijun
    # is less that 0.02 (or 0.002 for JPY pairs) and more than that on the last candle.
    # If so, it means they are crossing, indicating a trend turning point at the last completed candle
    if ctick1 * 10 ** decimalpip <= 2 and ctick2 * 10 ** decimalpip > 2:
        turningPoint = True
    if ctick2 * 10 ** decimalpip <= 2 and ctick3 * 10 ** decimalpip > 2:
        turningPoint = True
    # if ctick3 * 10 ** decimalpip <= 2 and ctick4 * 10 ** decimalpip > 2:
        # turningPoint = True

    # Let's see if the chiku touches the current price,
    # this would be considered as a weakening of the current trend
    # which is usually a good time to take out our gains (exit signal)
    chikouClose = False
    p = args['kjp']
    lastChiku = candles['chikou_span'][blocks - p - 1]
    if lastChiku >= candles['Low'][blocks - p - 1] and lastChiku <= candles['High'][blocks - p - 1]:
        chikouClose = True

    choice = None
    if cloudColor == "Red" and trend == "Down" and positionToCloud == "Under":
        choice = "Sell"
    if cloudColor == "Green" and trend == "Up" and positionToCloud == "Above":
        choice = "Buy"

    return {
        'Currency': currency,
        'cloudColor': cloudColor,
        'priceInCloud': priceInCloud,
        'positionToCloud': positionToCloud,
        'closetoCloud': closetoCloud,
        'trend': trend,
        'turningPoint': turningPoint,
        'chikouClose': chikouClose,
        'closeA': candles['senkou_span_a'][blocks - 1],
        'closeB': candles['senkou_span_b'][blocks - 1],
        'choice': choice
    }

def run(con):
    # currencies = ["GBP/USD"]
    currencies = ["GBP/JPY", "GBP/USD", "USD/CNH", "EUR/JPY", "USD/JPY", "CHF/JPY", "USD/CHF", "EUR/GBP", "NZD/USD", "USD/CAD", "AUD/JPY", "AUD/USD", "EUR/CHF", "GBP/CHF", "EUR/AUD", "EUR/CAD"] 
    mainPeriod = "m5"
    confirmationPeriod = "m15"
    validationPeriod = "m30"
    tendencySpan = 500
    pipWin = 5

    full = pd.DataFrame([], columns=['Currency', 'cloudColor', 'priceInCloud', 'positionToCloud', 'closetoCloud', 'trend', 'turningPoint', 'chikouClose', 'closeA', 'closeB', 'choice', 'tendencyValidation', 'MVA', 'DMI', 'type'])

    title = f'Pipwin : {pipWin} -- Period : {mainPeriod} -- Confirmation : {confirmationPeriod}'
    ctypes.windll.kernel32.SetConsoleTitleA(title)
    for currency in currencies:
        cand = con.get_candles(currency, period=mainPeriod, number=104, columns=['bids'])
        tendency = resultbycurrency(con, currency, mainPeriod, tendencySpan)
        cand.columns = ['Open', 'Close', 'High', 'Low']
        args = addToCandles(currency, cand)
        line = analyse(currency, cand, args)
        line.update(tendency)
        full = full.append([line])
    full = full.sort_values(by=['choice', 'turningPoint', 'tendencyValidation', 'DMI'])
    print(full)

    confirmation = None
    confirmation = pd.DataFrame([], columns=['Currency', 'cloudColor', 'priceInCloud', 'positionToCloud', 'closetoCloud', 'trend', 'turningPoint', 'chikouClose', 'closeA', 'closeB', 'choice'])
    for currency in currencies:
        cand = con.get_candles(currency, period=confirmationPeriod, number=104, columns=['bids'])
        cand.columns = ['Open', 'Close', 'High', 'Low']
        args = addToCandles(currency, cand)
        line = analyse(currency, cand, args)
        confirmation = confirmation.append([line])
    confirmation = confirmation.sort_values(by=['choice', 'turningPoint', 'positionToCloud'])
    print(confirmation)

    validation = None
    validation = pd.DataFrame([], columns=['Currency', 'cloudColor', 'priceInCloud', 'positionToCloud', 'closetoCloud', 'trend', 'turningPoint', 'chikouClose', 'closeA', 'closeB', 'choice'])
    for currency in currencies:
        cand = con.get_candles(currency, period=validationPeriod, number=104, columns=['bids'])
        cand.columns = ['Open', 'Close', 'High', 'Low']
        args = addToCandles(currency, cand)
        line = analyse(currency, cand, args)
        validation = validation.append([line])
    validation = validation.sort_values(by=['choice', 'turningPoint', 'positionToCloud'])
    print(validation)

    orders = con.get_open_positions().T

    print(f'Checking possible new trades on : {mainPeriod}')
    for index, row in full.iterrows():
        money = 20
        shortConf = False
        longConf = False
        if row['choice'] != None:
            print("------------------------------------------")
            print(row["Currency"], " trying to ", row['choice'])

            if row['priceInCloud'] == True:
                print("\tPrice in the cloud... don't...")
                continue

            if row['DMI'] == False:
                print("\tDMI indicates trades are unstable")
                continue

            if row['chikouClose'] == True:
                print("\tChikou in the price, no clear tendency !")
                continue

            print("\tChecking confirmation on short signal")
            for idx, r in confirmation.iterrows():
                if r['Currency'] == row['Currency']:
                    if r['choice'] == row['choice']:
                        # Confirmed signal between M1 and M5
                        print(f'\t\tConfirmed for {confirmationPeriod} ! Upping the investment')
                        money += 20
                        shortConf = True
            
            print("\tChecking confirmation on long signal")
            for idx, r in validation.iterrows():
                if r['Currency'] == row['Currency']:
                    if r['choice'] == row['choice']:
                        # Confirmed signal between M1 and M5
                        print(f'\t\tConfirmed for {validationPeriod} ! Upping the investment')
                        money += 40
                        longConf = True

            # If the signal is confirmed to be longer
            if shortConf == True or longConf == True:
                print(f'\tTendencies validate current trend, upping investment.')
                if row['tendencyValidation'] == True:
                    money *= 2

            # Now, make the trade
            print("\tOpening a ", row['choice'], "on ", row['Currency'], " for ", money)
            isBuy = row['choice'] == "Buy"

            if row['closetoCloud'] == True:
                print("\t\tPrice is too close to cloud, lowering investment !")
                money /= 2

            # Check if you already have a trade going for this
            found = False
            for o in orders:
                if orders[o]['currency'] == row['Currency']:
                    if orders[o]['isBuy'] == isBuy:
                        found = True
                        print("\t\tA trade is already open")
                    else:
                        print("\t\tCHANGE OF TREND, SWITCH AND CLOSE")
                        con.close_trade(trade_id=orders[o]['tradeId'], amount=orders[o]['amountK'])

            if found == True:
                continue

            if row['turningPoint'] == False:
                print("\tWaiting for a turning point !")
                # continue

            if found == False:
                # If fixed, change the pips too
                # isInPips = False
                # close = -15
                if row['positionToCloud'] == "Above":
                    close = row['closeB']
                else:
                    close = row['closeA']
                print("\tTrade confirmed and opening with an exit on ", close)
                # print("\tTrade confirmed and opening with an exit on -20 pips")
                # rt = con.open_trade(symbol=row['Currency'], is_buy=isBuy, amount=money, time_in_force='GTC', order_type='AtMarket', is_in_pips=True, trailing_step=10)
                tries = 3
                order = 0
                while order == 0 and tries > 0:
                    print("Trying to open a trade")
                    order = con.open_trade(symbol=row['Currency'], is_buy=isBuy, amount=money, time_in_force='GTC', order_type='AtMarket', is_in_pips=False, stop=close, trailing_step=10)
                    tries -= 1
                    time.sleep(1)
                print('Created order : ', order)
                if order == 0:
                    print("Just blunt creating ?")
                    order = con.open_trade(symbol=row['Currency'], is_buy=isBuy, amount=money, time_in_force='GTC', order_type='AtMarket')
                    print("Order? : ", o)
                # if rt != 0:
                    # oid = rt['tradeId']
                    # print("Oid : ", oid)
                    # Setting a trade limit depending on the potential outcome
                    # if shortConf:
                        # con.change_trade_stop_limit(oid, is_in_pips=True, is_stop=False, rate=10.0)
                    # elif longConf:
                        # con.change_trade_stop_limit(oid, is_in_pips=True, is_stop=False, rate=30.0)
                    # else:
                        # con.change_trade_stop_limit(oid, is_in_pips=True, is_stop=False, rate=5.0)

    print("Done")
    print("==========================================")
    print("Checking current orders")

    # Refresh with newly opened trades
    orders = con.get_open_positions().T

    for idx in orders:
        o = orders[idx]
        cur = o['currency']
        print("Order on ", cur)
        if o['limit'] == 0:
            con.change_trade_stop_limit(o['tradeId'], is_in_pips=True, is_stop=False, rate=5.0)
        data = None
        for index, row in full.iterrows():
            if row['Currency'] == cur:
                if row['chikouClose']:
                    print("\tFor ", o)
                    print("\tClose the trade, Chikou says nope")
                    con.close_trade(trade_id=o['tradeId'], amount=o['amountK'])
                if row['turningPoint'] == True:
                    currentTrade = o['isBuy']
                    if row['choice'] != None:
                        if (currentTrade and row['choice'] == "Sell") or (currentTrade == False and row['choice'] == "Buy"):
                            print("\tFor ", o)
                            print("\tClose the trade, turning point so tendency switch")
                            con.close_trade(trade_id=o['tradeId'], amount=o['amountK'])