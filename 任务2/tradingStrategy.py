# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import Utils
import time


pd.set_option('display.max_columns',10)
pd.set_option('display.width', 1000)


def DoubleMAStrategy(df, startDate, endDate, shortMA, mediumMA):
    strategyDf = df[startDate:endDate].copy()   # 策略DataFrame
    # 计算短期均线和长期均线
    shortMASeries = df['Close'].rolling(shortMA).mean()
    mediumMASeries = df['Close'].rolling(mediumMA).mean()
    
    # 计算金叉和死叉
    judge1 = shortMASeries < mediumMASeries
    judge2 = shortMASeries > mediumMASeries
    goldenCross = ~(judge1 | judge2.shift(1))
    deathCross = judge1 & judge2.shift(1)
    
    # 交易信号
    buySign = 1             # 买入信号
    sellSign = -1           # 卖出信号
    startOrEndSign = 0      # 交易上下限
    
    # 金叉第二日买入，死叉第二日卖出
    buyDate = goldenCross.shift(1)[startDate:endDate]   # 买入日期
    sellDate = deathCross.shift(1)[startDate:endDate]   # 卖出日期
    strategyDf.loc[buyDate, 'sign'] = buySign            # 写入买入信号
    strategyDf.loc[sellDate, 'sign'] = sellSign          # 写入卖出信号
    
    # 判断第一个交易日是否买入
    preStartDate = Utils.getPreDate(df, startDate)
    if shortMASeries[preStartDate] >= mediumMASeries[preStartDate]:
        strategyDf.loc[startDate, 'sign'] = buySign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign
    
    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign
    
    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])
    
    return strategyDf


def trading(strategyDf, startDate, endDate, initBalance=1000000, initHold=0):
    procedureRates = 5/10000    # 手续费
    hold = initHold             # 持有证券数
    balance = initBalance       # 资金余额
    beforeBalance = initBalance # 买入前的余额（计算平仓盈亏时使用）
    netAsset = balance + hold * strategyDf.loc[startDate, "Close"] # 净资产：资金剩余+持有证券数*收盘价
    
    # 增加列
    tradingDf = strategyDf.copy()
    zerosList = np.zeros(len(strategyDf))      # zeros
    nanList = np.full(len(strategyDf), np.nan) # nan
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


def getMAAndNetAsset(df, startDate, endDate, lowShortMA=1, highShortMA=15, lowmediumMA=20, highmediumMA=100, initMoney=1000000):
    data = []
    for shortMA in range(lowShortMA, highShortMA+1):
        for mediumMA in range(lowmediumMA, highmediumMA+1):
            strategyDf = DoubleMAStrategy(df, startDate, endDate, shortMA, mediumMA)
            tradingDf = trading(strategyDf, startDate, endDate)
            netAsset = tradingDf.iloc[-1]['netAsset']
            data.append([shortMA, mediumMA, netAsset])

    MAAndNetAssetDf = pd.DataFrame(data, columns=['shortMA', 'mediumMA', 'netAsset'])
    return MAAndNetAssetDf


def getTotalRate(initBalance, netAsset):
    totalRate = (netAsset - initBalance) / initBalance
    return totalRate


def getCompoundRate(totalRate, startDate, endDate):  
    # 将开始日期和结束日期转换为时间戳
    first =time.mktime((time.strptime(startDate, "%Y-%m-%d")))
    last = time.mktime((time.strptime(endDate, "%Y-%m-%d")))
    
    # 计算交易区间的天数
    days = (last - first) / (24 * 3600) + 1
    
    # 计算：年均收益率复利 <- 总收益率
    compoundRate = (totalRate + 1) ** (365.0/days) -1
    
    return compoundRate



