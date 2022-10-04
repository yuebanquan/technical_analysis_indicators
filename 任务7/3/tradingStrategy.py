# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import Utils
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def longMAAndDoubleMAStrategy(df, startDate, endDate, shortMA, mediumMA, longMA, showMA=False):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限
    strategyDf = df.copy()  # 策略DataFrame

    # 计算短期均线、中期均线和长期均线
    shortMA = df['Close'].rolling(shortMA).mean()
    mediumMA = df['Close'].rolling(mediumMA).mean()
    longMA = df['Close'].rolling(longMA).mean()

    # 是否显示MA
    if showMA == True:
        strategyDf['preClose'] = strategyDf['Close'].shift(1)
        strategyDf['preLongMA'] = longMA
        strategyDf['preLongMA'] = strategyDf['preLongMA'].shift(1)
        strategyDf['preShortMA'] = shortMA
        strategyDf['preShortMA'] = strategyDf['preShortMA'].shift(1)
        strategyDf['preMediumMA'] = mediumMA
        strategyDf['preMediumMA'] = strategyDf['preMediumMA'].shift(1)

    strategyDf = strategyDf[startDate:endDate]

    # 收盘价
    close = df['Close']

    goldenCross = (close > longMA) & (shortMA > mediumMA)
    judgeGoldenCross = ~goldenCross
    deathCross = ((close > longMA) & (shortMA < mediumMA)) | (close < longMA)
    judgeDeathCross = ~deathCross
    # 去重
    goldenCross = goldenCross & judgeGoldenCross.shift(1)
    deathCross = deathCross & judgeDeathCross.shift(1)

    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 判断第一个交易日是否买入
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    if (close[preStartDate] > longMA[preStartDate]) and (shortMA[preStartDate] > mediumMA[preStartDate]):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (close[preStartDate] < longMA[preStartDate]) or (
            (close[preStartDate] > longMA[preStartDate]) and (shortMA[preStartDate] < mediumMA[preStartDate])):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

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


def getMAAndNetAsset(df, startDate, endDate, lowShortMA=1, highShortMA=8, lowMediumMA=5, highMediumMA=21, lowLongMA=120,
                     highLongMA=180, initMoney=1000000):
    data = []

    for shortMA in range(lowShortMA, highShortMA + 1):
        for mediumMA in range(lowMediumMA, highMediumMA + 1):
            for longMA in range(lowLongMA, highLongMA + 1):
                # 短期均线一定小于中期均线和长期均线
                # 中期均线一定小于长期均线
                if (shortMA >= mediumMA) or (shortMA >= longMA) or (mediumMA >= longMA):
                    continue
                strategyDf = longMAAndDoubleMAStrategy(df, startDate, endDate, shortMA, mediumMA, longMA)
                tradingDf = trading(strategyDf, startDate, endDate)
                netAsset = tradingDf.iloc[-1]['netAsset']
                data.append([int(shortMA), int(mediumMA), int(longMA), netAsset])
                # print('shortMA = {}, mediumMA = {}, longMA = {}, netAsset = {}'.format(shortMA, mediumMA, longMA, netAsset))
    MAAndNetAssetDf = pd.DataFrame(data, columns=['shortMA', 'mediumMA', 'longMA', 'netAsset'])
    return MAAndNetAssetDf


def getBestStrategy(MAAndNetAssetDf):
    bestID = MAAndNetAssetDf['netAsset'].idxmax()
    bestShortMA = MAAndNetAssetDf.loc[bestID, 'shortMA']
    bestMediumMA = MAAndNetAssetDf.loc[bestID, 'mediumMA']
    bestLongMA = MAAndNetAssetDf.loc[bestID, 'longMA']
    bestNetAsset = MAAndNetAssetDf.loc[bestID, 'netAsset']
    bestStrategy = pd.Series([bestShortMA, bestMediumMA, bestLongMA, bestNetAsset],
                             index=['最佳短期均线', '最佳中期均线', '最佳长期均线', '本期净资产'])
    return bestStrategy


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


def slidingWindowTrading(df, backtestStartDate, backtestEndDate, sampleYear=8, lowShortMA=1, highShortMA=8,
                         lowMediumMA=5, highMediumMA=21, lowLongMA=120, highLongMA=180, initBalance=1000000):
    '''
    根据样本内年份，寻找最佳短期、中期、长期均线，并用到下一年进行回测
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

    bestMADf = pd.DataFrame(
        columns=['样本内数据年份数', '第iyear窗口', '最佳短期均线', '最佳中期均线', '最佳长期均线', '样本内净资产'])
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
        sampleMAAndNetAssetDf = getMAAndNetAsset(df, sampleStartDate, sampleEndDate, lowShortMA, highShortMA,
                                                 lowMediumMA, highMediumMA, lowLongMA, highLongMA)
        bestID = sampleMAAndNetAssetDf['netAsset'].idxmax()
        bestShortMA = sampleMAAndNetAssetDf.loc[bestID, 'shortMA']
        bestMediumMA = sampleMAAndNetAssetDf.loc[bestID, 'mediumMA']
        bestLongMA = sampleMAAndNetAssetDf.loc[bestID, 'longMA']
        sampleMostNetAsset = sampleMAAndNetAssetDf.loc[bestID, 'netAsset']
        bestMADf.loc[iyear] = [sampleYear, iyear, bestShortMA, bestMediumMA, bestLongMA, sampleMostNetAsset]
        # 将最佳MA放入滑动窗口进行回测
        slidingWindowStrategyDf = longMAAndDoubleMAStrategy(df, slidingWindowStartDate, slidingWindowEndDate,
                                                            bestShortMA, bestMediumMA, bestLongMA)

        newBacktestTradingDf = trading(slidingWindowStrategyDf, slidingWindowStartDate, slidingWindowEndDate, balance,
                                       hold)
        backtestTradingDf = pd.concat([backtestTradingDf, newBacktestTradingDf])

        # backtestTradingDf = backtestTradingDf.append(trading(slidingWindowStrategyDf, slidingWindowStartDate, slidingWindowEndDate, balance, hold))

        balance = backtestTradingDf.iloc[-1]['balance']
        hold = backtestTradingDf.iloc[-1]['hold']
        # netAsset = backtestTradingDf.iloc[-1]['netAsset']

    backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
    backtestTotalRate = getTotalRate(initBalance, backtestNetAsset)
    backtestCompoundRate = getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)

    revenues = pd.Series([sampleYear, backtestNetAsset, backtestCompoundRate],
                         index=['样本内数据年份数', '样本外净资产', '年均收益率复利'])

    return bestMADf, backtestTradingDf, revenues


def getNewTradingDf(df, tradingDf, startDate, endDate):
    # 扩充
    newTradingDf = pd.concat(
        [df[['Open', 'Close']][startDate:endDate], tradingDf[['sign', 'hold', 'balance', 'netAsset', 'profit']]],
        axis=1)

    # 填充hold & balance & netAsset 中的nan
    newTradingDf['hold'].fillna(method='ffill', inplace=True)  # 将前一个非nan填充进nan
    newTradingDf['balance'].fillna(method='ffill', inplace=True)  # 将前一个非nan填充进nan
    newTradingDf['netAsset'] = newTradingDf['balance'] + newTradingDf['hold'] * newTradingDf['Close']

    return newTradingDf


def getFR(newTradingDf, frFile, closeStd=923.45, netAssetStd=1000000):
    # closeStd = 923.45  # 第一个交易日的前一日收盘价
    # netAssetStd = 1000000

    FRDf = newTradingDf[['Close', 'netAsset']].copy()
    # 计算标的涨跌幅
    FRDf['closeFR'] = (FRDf['Close'] - closeStd) / closeStd
    # 计算净资产涨跌幅
    FRDf['netAssetFR'] = (FRDf['netAsset'] - netAssetStd) / netAssetStd
    # 画出每日净资产涨跌幅与标的涨跌幅对照图
    FRDf[['closeFR', 'netAssetFR']].plot()
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))  # Y轴显示为百分比
    plt.savefig(frFile)  # 保存图片
    plt.show()

    return FRDf


def getMaxDrawDown(newTradingDf):
    drawdown = (newTradingDf['netAsset'] - newTradingDf['netAsset'].cummax()) / newTradingDf['netAsset'].cummax()
    maxDrawDown = drawdown.min()
    return maxDrawDown


def getYearTotalRateDf(newTradingDf, startDate, endDate):
    # 计算开始年份和结束年份
    startYear = int(startDate[:4])
    endYear = int(endDate[:4])

    # 计算年收益率
    yearTotalRateDf = pd.DataFrame(columns=['netAsset'])
    yearTotalRateDf.index.name = 'Date'
    yearTotalRateDf.loc[newTradingDf.iloc[0].name, 'netAsset'] = newTradingDf.iloc[0]['netAsset']
    for year in range(startYear, endYear + 1):
        yearLastDate = Utils.getLastDate(newTradingDf, year)
        yearTotalRateDf.loc[yearLastDate, 'netAsset'] = newTradingDf.loc[yearLastDate, 'netAsset']

    # 计算年收益率
    yearTotalRateDf['yearTotalRate'] = yearTotalRateDf['netAsset'].pct_change(1)

    # 第一年与最后一年特殊判断
    # 第一年的第一个交易日不是那一年第一天,要将年收益率换算
    if not (yearTotalRateDf.iloc[0].name.is_year_start):
        yearStartDate = Utils.getFirstDate(newTradingDf, startYear)
        yearEndDate = Utils.getLastDate(newTradingDf, startYear)
        days = Utils.getDayNum(yearStartDate, yearEndDate)
        yearTotalRateDf.loc[yearEndDate, 'yearTotalRate'] = (yearTotalRateDf.loc[yearEndDate, 'yearTotalRate'] + 1) ** (
                365.0 / days) - 1
    # 最后一年的最后一个交易日不是那一年最后一天,要将年收益率换算
    if not (yearTotalRateDf.iloc[-1].name.is_year_end):
        yearStartDate = Utils.getFirstDate(newTradingDf, endYear)
        yearEndDate = Utils.getLastDate(newTradingDf, endYear)
        days = Utils.getDayNum(yearStartDate, yearEndDate)
        yearTotalRateDf.loc[yearEndDate, 'yearTotalRate'] = (yearTotalRateDf.loc[yearEndDate, 'yearTotalRate'] + 1) ** (
                365.0 / days) - 1

    return yearTotalRateDf


def getSharpRatio(yearTotalRateDf):
    yearTotalRate = yearTotalRateDf['yearTotalRate']  # 年收益率
    eRp = yearTotalRate.mean()  # 计算平均年收益率E(Rp)
    rf = 0.03  # 设置年化无风险利率Rf为3%
    # stdRp = np.std(yearTotalRate)  # 计算Rp的标准差σp(总体标准差:1/n)
    stdRp = yearTotalRate.std(ddof=0)  # 计算Rp的标准差σp(总体标准差:1/n)
    sharpRatio = (eRp - rf) / stdRp  # 夏普率
    return sharpRatio
