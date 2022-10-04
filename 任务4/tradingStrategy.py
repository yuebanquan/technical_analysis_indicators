# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import Utils
import time

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


def calculateEMA(close, span):
    # EMA = close.ewm(span=span, adjust=False).mean()

    EMA = close.copy()
    alpha = 2 / (span + 1)
    for i in range(len(close)):
        if i == 0:
            EMA[i] = EMA[i]
        if i > 0:
            EMA[i] = alpha * EMA[i] + (1 - alpha) * EMA[i-1]
    return EMA


def longEMAStrategy(df, startDate, endDate, longEMA, hold=0, showEMA=False, dropna=True):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限
    strategyDf = df.copy()  # 策略DataFrame

    # 计算长期EMA    
    longEMA = calculateEMA(df['Close'], longEMA)

    # 收盘价
    close = df['Close']

    # 是否显示EMA
    if showEMA:
        strategyDf['preClose'] = strategyDf['Close'].shift(1)
        strategyDf['preLongEMA'] = longEMA
        strategyDf['preLongEMA'] = strategyDf['preLongEMA'].shift(1)

    # 切片至交易区间
    strategyDf = strategyDf[startDate:endDate]

    # 计算金叉&死叉
    goldenCross = (close > longEMA) & (close <= longEMA).shift(1)
    deathCross = (close < longEMA) & (close >= longEMA).shift(1)
    # 买入&卖出日期为金叉&死叉的后一个交易日
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)
    # 写入买卖标志位
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 判断第一个交易日是否交易
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (close[preStartDate] > longEMA[preStartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (close[preStartDate] < longEMA[preStartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    if dropna:
        # 除去除交易上下限外不交易的日期
        strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


def shortEMAAndMediumEMAStrategy(df, startDate, endDate, shortEMA, mediumEMA, hold=0, showEMA=False, dropna=True):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限
    strategyDf = df.copy()  # 策略DataFrame

    # 计算长期EMA
    shortEMA = calculateEMA(df['Close'], shortEMA)
    mediumEMA = calculateEMA(df['Close'], mediumEMA)

    # 收盘价
    close = df['Close']

    # 是否显示EMA
    if showEMA:
        strategyDf['preClose'] = strategyDf['Close'].shift(1)
        strategyDf['preShortEMA'] = shortEMA
        strategyDf['preShortEMA'] = strategyDf['preShortEMA'].shift(1)
        strategyDf['preMediumEMA'] = mediumEMA
        strategyDf['preMediumEMA'] = strategyDf['preMediumEMA'].shift(1)

    # 切片至交易区间
    strategyDf = strategyDf[startDate:endDate]

    # 计算金叉&死叉
    goldenCross = (shortEMA > mediumEMA) & (shortEMA <= mediumEMA).shift(1)
    deathCross = (shortEMA < mediumEMA) & (shortEMA >= mediumEMA).shift(1)
    # 买入&卖出日期为金叉&死叉的后一个交易日
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 写入买卖标志位
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 判断第一个交易日是否交易
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (shortEMA[preStartDate] > mediumEMA[preStartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (shortEMA[preStartDate] < mediumEMA[preStartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    if dropna:
        # 除去除交易上下限外不交易的日期
        strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


def threeEMAStrategy(df, startDate, endDate, shortEMA, mediumEMA, longEMA, hold=0, showEMA=False, dropna=True):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限
    strategyDf = df.copy()  # 策略DataFrame

    # 计算长期EMA
    shortEMA = calculateEMA(df['Close'], shortEMA)
    mediumEMA = calculateEMA(df['Close'], mediumEMA)
    longEMA = calculateEMA(df['Close'], longEMA)

    # 收盘价
    close = df['Close']

    # 是否显示EMA
    if showEMA:
        strategyDf['preClose'] = strategyDf['Close'].shift(1)
        strategyDf['preShortEMA'] = shortEMA
        strategyDf['preShortEMA'] = strategyDf['preShortEMA'].shift(1)
        strategyDf['preMediumEMA'] = mediumEMA
        strategyDf['preMediumEMA'] = strategyDf['preMediumEMA'].shift(1)
        strategyDf['preLongEMA'] = longEMA
        strategyDf['preLongEMA'] = strategyDf['preLongEMA'].shift(1)

    # 切片至交易区间
    strategyDf = strategyDf[startDate:endDate]

    # 计算金叉&死叉
    goldenCross = (close > longEMA) & (shortEMA > mediumEMA)
    judgeGoldenCross = ~goldenCross
    deathCross = ((close > longEMA) & (shortEMA < mediumEMA)) | (close < longEMA)
    judgeDeathCross = ~deathCross
    # 去重
    goldenCross = goldenCross & judgeGoldenCross.shift(1)
    deathCross = deathCross & judgeDeathCross.shift(1)
    # 买入&卖出日期为金叉&死叉的后一个交易日
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 写入买卖标志位
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 判断第一个交易日是否交易
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if ((close[preStartDate] > longEMA[preStartDate]) and (shortEMA[preStartDate] > mediumEMA[preStartDate])) and (
            hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif ((close[preStartDate] < longEMA[preStartDate]) or (
            (close[preStartDate] > longEMA[preStartDate]) and (shortEMA[preStartDate] < mediumEMA[preStartDate]))) and (
            hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    if dropna:
        # 除去除交易上下限外不交易的日期
        strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


def trading(strategyDf, startDate, endDate, initBalance=1000000, initHold=0):
    procedureRates = 5 / 10000  # 手续费
    hold = initHold  # 持有证券数
    balance = initBalance  # 资金余额
    beforeBalance = initBalance  # 买入前的余额（计算平仓盈亏时使用）
    netAsset = balance + hold * strategyDf.loc[startDate, "Close"]  # 净资产：资金剩余+持有证券数*收盘价

    # 增加列
    tradingDf = strategyDf.copy()
    zerosList = np.zeros(len(strategyDf))  # zeros
    nanList = np.full(len(strategyDf), np.nan)  # nan
    tradingDf['hold'] = nanList
    tradingDf['balance'] = zerosList
    tradingDf['netAsset'] = zerosList
    tradingDf['profit'] = zerosList

    # 初始化：第一个交易日的数据
    tradingDf.loc[startDate, 'hold'] = hold
    tradingDf.loc[startDate, 'balance'] = initBalance
    tradingDf.loc[startDate, 'netAsset'] = netAsset

    # 交易信号
    buySign = 1
    sellSign = -1
    startOrEndSign = 0

    # 向量化
    openList = tradingDf['Open'].values
    closeList = tradingDf['Close'].values
    signList = tradingDf['sign'].values
    holdList = tradingDf['hold'].values
    balanceList = tradingDf['balance'].values
    netAssetList = tradingDf['netAsset'].values
    profitList = tradingDf['profit'].values

    # 开始交易
    for i in range(0, len(tradingDf)):
        if signList[i] == buySign:
            beforeBalance = balance
            buynum = balance // (openList[i] * (1 + procedureRates))
            # 资金余额可以购买
            if buynum != 0:
                hold = holdList[i] = hold + buynum
                balance = balanceList[i] = balance - buynum * openList[i] * (1 + procedureRates)
                netAsset = netAssetList[i] = balance + buynum * openList[i]
        elif signList[i] == sellSign:
            balance = balanceList[i] = balance + hold * openList[i] * (1 - procedureRates)
            netAsset = netAssetList[i] = balance
            if hold != 0:
                profitList[i] = balance - beforeBalance
            hold = holdList[i] = 0
        elif signList[i] == startOrEndSign:
            holdList[i] = hold
            balanceList[i] = balance
            netAssetList[i] = balance + hold * closeList[i]

    tradingDf['hold'] = holdList
    tradingDf['balance'] = balanceList
    tradingDf['netAsset'] = netAssetList
    tradingDf['balance'] = balanceList
    tradingDf['profit'] = profitList

    return tradingDf


def getEMAAndNetAsset1(df, startDate, endDate, lowLongEMA=120, highLongEMA=240):
    data = []
    for longEMA in range(lowLongEMA, highLongEMA + 1):
        strategyDf = longEMAStrategy(df, startDate, endDate, longEMA)
        tradingDf = trading(strategyDf, startDate, endDate)
        netAsset = tradingDf.iloc[-1]['netAsset']
        data.append([longEMA, netAsset])
        # print('longEMA = {}, netAsset = {}'.format(longEMA, netAsset))

    EMAAndNetAssetDf = pd.DataFrame(data, columns=['longEMA', 'netAsset'])
    return EMAAndNetAssetDf


def getEMAAndNetAsset2(df, startDate, endDate, lowShortEMA=1, highShortEMA=15, lowMediumEMA=20, highMediumEMA=100):
    data = []

    for shortEMA in range(lowShortEMA, highShortEMA + 1):
        for mediumEMA in range(lowMediumEMA, highMediumEMA + 1):
            strategyDf = shortEMAAndMediumEMAStrategy(df, startDate, endDate, shortEMA, mediumEMA)
            tradingDf = trading(strategyDf, startDate, endDate)
            netAsset = tradingDf.iloc[-1]['netAsset']
            data.append([shortEMA, mediumEMA, netAsset])
            print('shortEMA = {}, mediumEMA={}, netAsset = {}'.format(shortEMA, mediumEMA, netAsset))

    EMAAndNetAssetDf = pd.DataFrame(data, columns=['shortEMA', 'mediumEMA', 'netAsset'])
    return EMAAndNetAssetDf


def getMAAndNetAsset3(df, startDate, endDate, lowShortEMA=1, highShortEMA=8, lowMediumEMA=5, highMediumEMA=21,
                      lowLongEMA=120, highLongEMA=180):
    data = []
    for longEMA in range(lowLongEMA, highLongEMA + 1):
        for mediumEMA in range(lowMediumEMA, highMediumEMA + 1):
            for shortEMA in range(lowShortEMA, highShortEMA + 1):
                # 短期均线一定小于中期均线和长期均线
                # 中期均线一定小于长期均线
                if (shortEMA >= mediumEMA) or (shortEMA >= longEMA) or (mediumEMA >= longEMA):
                    continue
                strategyDf = threeEMAStrategy(df, startDate, endDate, shortEMA, mediumEMA, longEMA)
                tradingDf = trading(strategyDf, startDate, endDate)
                netAsset = tradingDf.iloc[-1]['netAsset']
                data.append([shortEMA, mediumEMA, longEMA, netAsset])
                # print('shortEMA = {}, mediumEMA = {}, longEMA = {}, netAsset = {}'.format(shortEMA, mediumEMA, longEMA, netAsset))
                print('shortEMA = {}, mediumEMA = {}, longEMA = {}, netAsset = {}'.format(shortEMA, mediumEMA, longEMA,
                                                                                          netAsset),
                      end="\r")  # object为需要打印的内容
                MAAndNetAssetDf = pd.DataFrame(data, columns=['shortEMA', 'mediumEMA', 'longEMA', 'netAsset'])
    return MAAndNetAssetDf


def getBestStrategy1(EMAAndNetAssetDf, showBestLongEMA=True, showBestNetAsset=True):
    bestID = EMAAndNetAssetDf['netAsset'].idxmax()
    bestLongEMA = EMAAndNetAssetDf.loc[bestID, 'longEMA']
    bestNetAsset = EMAAndNetAssetDf.loc[bestID, 'netAsset']

    if showBestLongEMA == True and showBestNetAsset == False:
        return bestLongEMA
    elif showBestLongEMA == False and showBestNetAsset == True:
        return bestNetAsset
    else:
        return bestLongEMA, bestNetAsset


def getBestStrategy2(EMAAndNetAssetDf):
    bestID = EMAAndNetAssetDf['netAsset'].idxmax()
    bestShortEMA = EMAAndNetAssetDf.loc[bestID, 'shortEMA']
    bestMediumEMA = EMAAndNetAssetDf.loc[bestID, 'mediumEMA']
    bestNetAsset = EMAAndNetAssetDf.loc[bestID, 'netAsset']
    return bestShortEMA, bestMediumEMA, bestNetAsset


def getBestStrategy3(EMAAndNetAssetDf):
    bestID = EMAAndNetAssetDf['netAsset'].idxmax()
    bestShortEMA = EMAAndNetAssetDf.loc[bestID, 'shortEMA']
    bestMediumEMA = EMAAndNetAssetDf.loc[bestID, 'mediumEMA']
    bestLongEMA = EMAAndNetAssetDf.loc[bestID, 'longEMA']
    bestNetAsset = EMAAndNetAssetDf.loc[bestID, 'netAsset']
    return bestShortEMA, bestMediumEMA, bestLongEMA, bestNetAsset


def getTotalRate(initBalance, netAsset):
    totalRate = (netAsset - initBalance) / initBalance
    return totalRate


def getCompoundRate(totalRate, startDate, endDate):
    # 将开始日期和结束日期转换为时间戳
    first = time.mktime((time.strptime(startDate, "%Y-%m-%d")))
    last = time.mktime((time.strptime(endDate, "%Y-%m-%d")))

    # 计算交易区间的天数
    days = (last - first) / (24 * 3600) + 1

    # 计算：年均收益率复利 <- 总收益率
    compoundRate = (totalRate + 1) ** (365.0 / days) - 1

    return compoundRate


def slidingWindowTrading(df, backtestStartDate, backtestEndDate, sampleYear=8, lowShortEMA=1, highShortEMA=8,
                         lowMediumEMA=5, highMediumEMA=21, lowLongEMA=120, highLongEMA=180, initBalance=1000000):
    '''
    根据样本内年份，寻找最佳短期、中期、长期EMA，并用到下一年进行回测
    '''
    balance = initBalance  # 现金余额
    # netAsset = initBalance
    hold = 0

    backtestStartYear = int(backtestStartDate[:4])  # 回测开始年份
    backtestEndYear = int(backtestEndDate[:4])  # 回测结束年份
    backtestYear = backtestEndYear - backtestStartYear + 1
    # print(backtestYear)
    sampleStartYear = backtestStartYear - sampleYear  # 样本开始年份
    sampleEndYear = backtestStartYear - 1  # 样本结束年份

    # 计算设计年份的第一个交易日和最后一个交易日
    yearDf = pd.DataFrame(columns=['startDate', 'endDate'])
    for year in range(sampleStartYear, backtestEndYear + 1):
        yearDf.loc[year] = [Utils.getFirstDate(df, year), Utils.getLastDate(df, year)]

    bestEMADf = pd.DataFrame(
        columns=['样本内数据年份数', '第iyear窗口', '最佳短期EMA', '最佳中期EMA', '最佳长期EMA', '样本内净资产'])
    backtestTradingDf = pd.DataFrame(columns=['Open', 'Close', 'sign', 'hold', 'balance', 'netAsset', 'profit'])

    for iyear in range(0, backtestYear):
        sampleStartDate = yearDf.loc[sampleStartYear + iyear, 'startDate']
        sampleEndDate = yearDf.loc[sampleEndYear + iyear, 'endDate']
        slidingWindowStartDate = yearDf.loc[backtestStartYear + iyear, 'startDate']
        slidingWindowEndDate = yearDf.loc[backtestStartYear + iyear, 'endDate']
        print(slidingWindowStartDate + " to " + slidingWindowEndDate)
        # print(sampleStartDate)
        # print(sampleEndDate)
        # print(" ")

        # 找最佳MA
        sampleMAAndNetAssetDf = getMAAndNetAsset3(df, sampleStartDate, sampleEndDate, lowShortEMA, highShortEMA,
                                                  lowMediumEMA, highMediumEMA, lowLongEMA, highLongEMA)
        bestShortEMA, bestMediumEMA, bestLongEMA, sampleMostNetAsset = getBestStrategy3(sampleMAAndNetAssetDf)
        bestEMADf.loc[iyear] = [sampleYear, iyear, bestShortEMA, bestMediumEMA, bestLongEMA, sampleMostNetAsset]

        # """
        # """
        # if iyear == 5:
        #     sampleMAAndNetAssetDf.to_csv(r"./2019.csv")
        #     break

        # 将最佳MA放入滑动窗口进行回测
        slidingWindowStrategyDf = threeEMAStrategy(df, slidingWindowStartDate, slidingWindowEndDate, bestShortEMA,
                                                   bestMediumEMA, bestLongEMA, hold=hold, showEMA=True)

        newBacktestTradingDf = trading(slidingWindowStrategyDf, slidingWindowStartDate, slidingWindowEndDate, balance,
                                       hold)
        backtestTradingDf = pd.concat([backtestTradingDf, newBacktestTradingDf])

        balance = backtestTradingDf.iloc[-1]['balance']
        hold = backtestTradingDf.iloc[-1]['hold']
        # netAsset = backtestTradingDf.iloc[-1]['netAsset']

    backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
    backtestTotalRate = getTotalRate(initBalance, backtestNetAsset)
    backtestCompoundRate = getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)

    revenues = pd.Series([sampleYear, backtestNetAsset, backtestCompoundRate],
                         index=['样本内数据年份数', '样本外净资产', '年均收益率复利'])

    return bestEMADf, backtestTradingDf, revenues
