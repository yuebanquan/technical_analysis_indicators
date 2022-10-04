# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import Utils
import time

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


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
