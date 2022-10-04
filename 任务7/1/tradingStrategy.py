# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import Utils
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def strategy(df, startDate, endDate, MA, initMoney=1000000, hold=0):
    """
    做多（手续费万分之五）：
    如果当日收盘价大于240日均线，第二日以开盘价买入；
    如果当日收盘价小于240日均线，第二日以开盘价卖出。
    
    Parameters
    ----------
    df : DataFrame
        股票数据.
    startDate : str
        交易区间下限.
    endDate : str
        交易区间上限.
    MA : int
        长期均线.
    initMoney : float, optional
        初始资金. The default is 1000000.
    hold : int, optional
        初始持有证券数. The default is 0.

    Returns
    -------
    df : DataFrame
        每个成交日期的数据.
    """
    # 交易中重要的变量
    hold = hold  # 持有证券数
    balance = initMoney  # 资金余额
    beforeMoney = initMoney  # 买入前的余额（计算平仓盈亏时使用）
    netAsset = balance + hold * df.loc[startDate, "Close"]  # 净资产：资金剩余+持有证券数*收盘价
    procedureRates = 5 / 10000  # 手续费

    # 初始化：新增列
    # df.insert(loc=len(df.columns), column='MA', value=df['Close'].rolling(MA).mean()) # 长期均线
    # df.insert(loc=len(df.columns), column='sign', value=np.nan)                # 买卖信号
    # df.insert(loc=len(df.columns), column='hold', value=np.zeros(len(df)))     # 持有证券数量
    # df.insert(loc=len(df.columns), column='balance', value=np.zeros(len(df)))  # 资金余额
    # df.insert(loc=len(df.columns), column='netAsset', value=np.zeros(len(df))) # 净资产
    # df.insert(loc=len(df.columns), column='profit', value=np.zeros(len(df)))   # 平仓盈亏
    # 初始化：新增列
    MAList = df['Close'].rolling(MA).mean()  # 长期均线
    zerosList = np.zeros(len(df))  # zeros
    nanList = np.full(len(df), np.nan)  # nan
    df['MA'] = MAList
    df['sign'] = nanList
    df['hold'] = zerosList
    df['balance'] = zerosList
    df['netAsset'] = zerosList
    df['profit'] = zerosList
    # 初始化：第一个交易日的数据
    df.loc[startDate, 'hold'] = hold
    df.loc[startDate, 'balance'] = initMoney
    df.loc[startDate, 'netAsset'] = netAsset

    # 数据清洗，去除没有长期均线的数据
    df = df.dropna(subset=['MA'])

    # 获取交易区间前一交易日
    preStartDate = Utils.getPreDate(df, startDate)

    # 对股票数据切片，取交易区间的前一日+交易区间的数据
    df = df.loc[preStartDate:endDate]

    # 计算交易信号
    startOrEndSign = 0  # 初始/结束信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    # 遍历df
    # 向量化，方便遍历
    closeList = df['Close'].values
    MAList = df['MA'].values
    signList = df['sign'].values
    for i in range(0, len(df) - 1):
        # 判断第一日是否交易（用第一日的前一交易日判断）
        if i == 0:
            # 只要前一日的收盘价>=MA，买入
            if closeList[i] >= MAList[i]:
                signList[i + 1] = buySign
            else:
                signList[i + 1] = startOrEndSign
        else:
            if closeList[i - 1] < MAList[i - 1] and closeList[i] >= MAList[i]:
                signList[i + 1] = buySign
            elif closeList[i - 1] > MAList[i - 1] and closeList[i] <= MAList[i]:
                signList[i + 1] = sellSign

        # 如果最后一个交易日不交易，买卖信号置为‘0’
        if np.isnan(signList[-1]):
            signList[-1] = startOrEndSign

    # 将买卖信号写入df中，并除去不交易的日期（保留交易区间上下限）
    df['sign'] = signList
    df = df.dropna(subset=['sign'])

    # 交易
    # 向量化，方便遍历
    openList = df['Open'].values
    closeList = df['Close'].values
    signList = df['sign'].values
    holdList = df['hold'].values
    balanceList = df['balance'].values
    netAssetList = df['netAsset'].values
    balanceList = df['balance'].values
    profitList = df['profit'].values

    for i in range(0, len(df)):
        if signList[i] == buySign:
            beforeMoney = balance
            buynum = balance // (openList[i] * (1 + procedureRates))
            hold = holdList[i] = hold + buynum
            balance = balanceList[i] = balance - buynum * openList[i] * (1 + procedureRates)
            netAsset = netAssetList[i] = balance + buynum * openList[i]
        elif signList[i] == sellSign:
            balance = balanceList[i] = balance + hold * openList[i] * (1 - procedureRates)
            netAsset = netAssetList[i] = balance
            profitList[i] = balance - beforeMoney
            hold = holdList[i] = 0
        elif signList[i] == startOrEndSign:
            holdList[i] = hold
            balanceList[i] = balance
            netAssetList[i] = balance + hold * closeList[i]

    # 将数据写入df
    df['hold'] = holdList
    df['balance'] = balanceList
    df['netAsset'] = netAssetList
    df['balance'] = balanceList
    df['profit'] = profitList

    return df


def trading(strategyDf, startDate, endDate, initBalance=1000000, initHold=0):
    procedureRates = 5 / 10000  # 手续费
    hold = initHold  # 持有证券数
    balance = initBalance  # 资金余额
    beforeBalance = initBalance  # 买入前的余额（计算平仓盈亏时使用）
    netAsset = balance + hold * strategyDf.loc[startDate, "Close"]  # 净资产：资金剩余+持有证券数*收盘价

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

    for i in range(0, len(tradingDf)):
        if signList[i] == buySign:
            beforeBalance = balance
            buynum = balance // (openList[i] * (1 + procedureRates))
            hold = holdList[i] = hold + buynum
            balance = balanceList[i] = balance - buynum * openList[i] * (1 + procedureRates)
            netAsset = netAssetList[i] = balance + buynum * openList[i]
        elif signList[i] == sellSign:
            balance = balanceList[i] = balance + hold * openList[i] * (1 - procedureRates)
            netAsset = netAssetList[i] = balance
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


def getMAAndNetAsset(df, startDate, endDate, lowMA=120, highMA=240, initMoney=1000000):
    """
    通过MA区间，求相应MA的交易后净资产

    Parameters
    ----------
    df : DataFrame
        股票数据.
    startDate : str
        交易区间下限.
    endDate : str
        交易区间上限.
    lowMA : int, optional
        MA下限. The default is 120.
    highMA : int, optional
        MA上限. The default is 240.
    initMoney : TYPE, optional
        初始持有证券数. The default is 1000000.

    Returns
    -------
    MAAndNetAssetDf : DataFrame
        相应MA的交易后净资产.

    """
    data = []
    for i in range(lowMA, highMA + 1):
        # netAsset = strategy(df, startDate, endDate, i).iloc[-1]['netAsset']
        strategyDf = strategy(df, startDate, endDate, i)
        netAsset = strategyDf.iloc[-1]['netAsset']
        data.append([i, netAsset])
    MAAndNetAssetDf = pd.DataFrame(data, columns=['MA', 'netAsset'], dtype=object)
    MAAndNetAssetDf.set_index('MA', inplace=True)
    return MAAndNetAssetDf


def getBestMA(df, startDate, endDate, lowMA=120, highMA=240, initMoney=1000000):
    """
    通过MA区间，求相最佳MA

    Parameters
    ----------
    df : DataFrame
        股票数据.
    startDate : str
        交易区间下限.
    endDate : str
        交易区间上限.
    lowMA : int, optional
        MA下限. The default is 120.
    highMA : int, optional
        MA上限. The default is 240.
    initMoney : TYPE, optional
        初始持有证券数. The default is 1000000.

    Returns
    -------
    bestMA : int
        最佳MA.

    """
    data = []
    for i in range(lowMA, highMA + 1):
        netAsset = strategy(df, startDate, endDate, i).iloc[-1]['netAsset']
        data.append([i, netAsset])
    MAAndNetAssetDf = pd.DataFrame(data, columns=['MA', 'netAsset'], dtype=object)
    MAAndNetAssetDf.set_index('MA', inplace=True)
    bestMA = MAAndNetAssetDf.astype('int64').idxmax()[0]
    return bestMA


def getTotalRate(initMoney, netAsset):
    totalRate = (netAsset - initMoney) / initMoney
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
