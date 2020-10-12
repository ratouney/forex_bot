import fxcmpy
import ctypes
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
    'decimalpip': 5,
}

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

    # Trying to see what the general trend indicates
    # given the tenkan/kijun moving averages
    trend = None
    if candles['tenkan_sen'][blocks - 1] > candles['kijun_sen'][blocks - 1]:
        trend = "Up"
    else:
        trend = "Down"

    # Are we on a turning point
    turningPoint = False
    ctick = abs(candles['tenkan_sen'][blocks - 2] - candles['kijun_sen'][blocks - 2])
    ctick2 = abs(candles['tenkan_sen'][blocks - 1] - candles['kijun_sen'][blocks - 1])
    # Taking the pre-last candle, check if the difference between the Tenkan and Kijun
    # is less that 0.02 (or 0.002 for JPY pairs) and more than that on the last candle.
    # If so, it means they are crossing, indicating a trend turning point at the last completed candle
    if ctick * 10 ** decimalpip <= 2 and ctick2 * 10 ** decimalpip > 2:
        turningPoint = True

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
        'trend': trend,
        'turningPoint': turningPoint,
        'chikouClose': chikouClose,
        'closeA': candles['senkou_span_a'][blocks - 1],
        'closeB': candles['senkou_span_b'][blocks - 1],
        'choice': choice
    }




def run(con):
    currencies = ["GBP/JPY", "GBP/USD", "USD/CNH", "EUR/JPY", "USD/JPY", "CHF/JPY", "USD/CHF", "EUR/GBP", "NZD/USD", "USD/CAD", "BTC/USD"] 
    # currency = "XAU/USD"
    mainPeriod = "m5"
    confirmationPeriod = "m15"
    pipWin = 10

    full = pd.DataFrame([], columns=['Currency', 'cloudColor', 'priceInCloud', 'positionToCloud', 'trend', 'turningPoint', 'chikouClose', 'closeA', 'closeB', 'choice'])

    title = f'Pipwin : {pipWin} -- Period : {mainPeriod} -- Confirmation : {confirmationPeriod}'
    ctypes.windll.kernel32.SetConsoleTitleA(title)
    for currency in currencies:
        cand = con.get_candles(currency, period=mainPeriod, number=104, columns=['bids'])
        cand.columns = ['Open', 'Close', 'High', 'Low']
        args = addToCandles(currency, cand)
        line = analyse(currency, cand, args)
        full = full.append([line])
    full = full.sort_values(by=['choice', 'turningPoint', 'positionToCloud'])
    print(full)

    confirmation = None
    confirmation = pd.DataFrame([], columns=['Currency', 'cloudColor', 'priceInCloud', 'positionToCloud', 'trend', 'turningPoint', 'chikouClose', 'closeA', 'closeB', 'choice'])
    for currency in currencies:
        cand = con.get_candles(currency, period=confirmationPeriod, number=104, columns=['bids'])
        cand.columns = ['Open', 'Close', 'High', 'Low']
        args = addToCandles(currency, cand)
        line = analyse(currency, cand, args)
        confirmation = confirmation.append([line])
    confirmation = confirmation.sort_values(by=['choice', 'turningPoint', 'positionToCloud'])
    print(confirmation)

    orders = con.get_open_positions().T

    print("==========================================")
    print("Checking current orders")
    for idx in orders:
        o = orders[idx]
        cur = o['currency']
        data = None
        for index, row in full.iterrows():
            if row['Currency'] == cur:
                if row['chikouClose']:
                    print("\tFor ", o)
                    print("\tClose the trade, Chikou says nope")
                    con.close_trade(trade_id=o['tradeId'], amount=o['amountK'])
    print("Done")
    print("==========================================")

    print("Checking possible new trades")
    for index, row in full.iterrows():
        money = 5
        if row['choice'] != None:
            print("------------------------------------------")
            print(row["Currency"], " trying to ", row['choice'])

            print("\tChecking confirmation on longer signal")
            for idx, r in confirmation.iterrows():
                if r['Currency'] == row['Currency']:
                    if r['choice'] == row['choice']:
                        # Confirmed signal between M1 and M5
                        print("\t\tConfirmed ! Upping the investment")
                        money += 25

            # Now, make the trade
            print("\tOpening a ", row['choice'], "on ", row['Currency'], " for ", money)
            isBuy = row['choice'] == "Buy"

            # Check if you already have a trade going for this

            found = False
            for o in orders:
                if orders[o]['currency'] == row['Currency']:
                    if orders[o]['isBuy'] == isBuy:
                        found = True
                        print("\t\tA trade is already open")
                        break
                    else:
                        print("\t\tCHANGE OF TREND, SWITCH AND CLOSE")
                        break

            if row['turningPoint'] == False:
                print("\tWaiting for a turning point !")
                continue

            if found == False:
                close = None
                if row['positionToCloud'] == "Above":
                    close = row['closeA']
                else:
                    close = row['closeB']
                print("\tTrade confirmed and opening with an exit on ", close)
                con.open_trade(symbol=row['Currency'], is_buy=isBuy, amount=money, time_in_force='GTC', order_type='AtMarket', is_in_pips=False, stop=close, trailing_step=10)
            