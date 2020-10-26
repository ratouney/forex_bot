import fxcmpy
import mplfinance as mpf
import pandas as pd
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time
# from canbuy import buying

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
        print("Warning : the market is in oversell, we should consider buying aiming long")
        redline = True
    if (z >= int(periodN2 - periodN2 / 2.5)):
        print("Warning : the market is in overbought, we should consider selling aiming long")
        redline = True
    return redline



def indicMVA(MVA1, MVA2, MVA3, periodN):
    redline = True
    indic = False
    for i in range (int(periodN / 100)):
        if (MVA2[0][MVA2[0].size - i - 1]) < (MVA3[0][MVA3[0].size - i - 1]):
            indic = True
            redline = False
    if (indic == True):
        print("can't buy (MVA2 < MVA3)")
        indic = False
    for y in range (int(periodN / 100)):
        if (MVA1[0][MVA1[0].size - i - 1]) < (MVA2[0][MVA2[0].size - i - 1]):
            redline = False
            indic = True
    if (indic == True):
        print("can't buy (MVA1 < MVA2)")
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

    
def resultbycurrency(con, currency):

    periodN = 1000
    data = con.get_candles(currency, period='m15', number=periodN)
    result = 0

    MVA1 = createtendency(data, int(periodN / 20), periodN)
    MVA2 = createtendency(data, int(periodN / 10), periodN)
    MVA3 = createtendency(data, int(periodN / 5), periodN)
    rsi = rsicalculation(data, periodN)
    dmi = dmicalculation(data, periodN)
    print("-------------------------------")
    print(currency)
    redline = indicMVA(MVA1, MVA2, MVA3, periodN)
    redline = indicDMI(periodN, 'm15', currency, redline, con)
    if (redline == True):
        print("You can buy now on " + currency)
        result = 1
        redline = False
    redline = indicRSI(periodN, 'm15', currency, redline, con)
    return result 


def display(data, MVA1, MVA2, MVA3, rsi, dmi, periodN):

    dataX = np.arange(periodN)
    dataY1 = data.loc[:, ['bidopen']].to_numpy()
    dataY2 = data.loc[:, ['bidclose']].to_numpy()
    dataY = (dataY1 + dataY2) / 2

##########################################################
# graphics output section
    period1 = int(periodN / 20)
    period2 = int(periodN / 10)
    period3 = int(periodN / 5)
    graphWidth = 1600
    graphHeight = 800
    fig, (axes1, axes2) = plt.subplots(2, figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    axes1.plot(dataX, dataY,  'D')
    axes1.plot(dataX, rsi[0], label = "OverSell")
    axes1.plot(dataX, rsi[1], label = "OverBought")
    axes1.plot(MVA1[1], MVA1[0], label = str(period1) + " periods")
    axes1.plot(MVA2[1], MVA2[0], label = str(period2) + " periods")
    axes1.plot(MVA3[1], MVA3[0], label = str(period3) + " periods")
    axes1.legend(loc="upper left")
    axes1.set_xlabel('X Data') # X axis data label
    axes1.set_ylabel('price EUR/USD') # Y axis data label
    axes2.plot(dataX, dmi[0], label = "DMI-")
    axes2.plot(dataX, dmi[1], label = "DMI+")
    axes2.plot(dataX, np.full(periodN, 0), label = "MOY")
    axes2.plot(dataX, np.full(periodN, -21), label = "5 sell in a row")
    axes2.plot(dataX, np.full(periodN, 21), label = "5 sell in a row")
    axes2.legend(loc="upper left")
    plt.show()
    plt.close('all') # clean up after using pyplot

def botcheck(currency):
    # ici tu peux faire appel à mes fonctions indic pour qu'elles te sortent
    return(True)

def buying(canbuy, con):

    periodN = 500
    data = con.get_candles('EUR/USD', period='m1', number=periodN)
    stop = False
    MVA1 = createtendency(data, int(periodN / 20), periodN)
    MVA2 = createtendency(data, int(periodN / 10), periodN)
    MVA3 = createtendency(data, int(periodN / 5), periodN)
    rsi = rsicalculation(data, periodN)
    dmi = dmicalculation(data, periodN)

    openP = con.get_open_positions().T
    # print(openP)
    for i in range (canbuy.size):
        order = con.create_market_buy_order(canbuy[i], 200)
    tradeIds = con.get_open_trade_ids()
    print(tradeIds)
    tradeId = np.array(tradeIds)
    for i in range (tradeId.size):
        print("oui")
        con.change_trade_stop_limit(tradeId[i], is_in_pips=False,
                            is_stop=False, rate=100) # j'ai pas réussi à mettre des trailing stop faudrait le faire
    while (stop == False):   
        stop = botcheck(canbuy)
        # sleep(60)
    display(data, MVA1, MVA2, MVA3, rsi, dmi, periodN)

def run(con):

    periodN = 500
    canbuy = np.array([''])
    # # in the week
    data = con.get_candles('EUR/USD', period='H1', number=periodN)

    MVA1 = createtendency(data, int(periodN / 20), periodN)
    MVA2 = createtendency(data, int(periodN / 10), periodN)
    MVA3 = createtendency(data, int(periodN / 5), periodN)
    rsi = rsicalculation(data, periodN)
    dmi = dmicalculation(data, periodN)

    currencies = np.array(['EUR/USD', 'XAU/USD', 'GER30', 'USD/JPY', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'BTC/USD'])
    for i in range (currencies.size):
        result = resultbycurrency(con, currencies[i])
        if (result == 1):
            canbuy = np.append(canbuy, currencies[i])
    buying(canbuy, con)
    # display(data, MVA1, MVA2, MVA3, rsi, dmi, periodN)

    
