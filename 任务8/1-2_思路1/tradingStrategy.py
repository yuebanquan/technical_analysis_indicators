import numpy as np
import pandas as pd
import Utils
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


# 单均线策略
def strategy1(df, startDate, endDate, MA, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    close = df['Close']
    ma = df['Close'].rolling(MA).mean()

    # 取交易日期
    # 计算金叉 & 死叉、买入日期 & 卖出日期
    goldenCross = (close > ma) & (close <= ma).shift(1)
    deathCross = (close < ma) & (close >= ma).shift(1)
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (close[preStartDate] > ma[preStartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (close[preStartDate] < ma[preStartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# 双均线策略
def strategy2(df, startDate, endDate, shortMA, mediumMA, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    close = df['Close']
    shortMa = df['Close'].rolling(shortMA).mean()
    mediumMa = df['Close'].rolling(mediumMA).mean()

    # 取交易日期
    # 计算金叉 & 死叉、买入日期 & 卖出日期
    judge1 = shortMa < mediumMa
    judge2 = shortMa > mediumMa
    goldenCross = ~(judge1 | judge2.shift(1))
    deathCross = judge1 & judge2.shift(1)

    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (shortMa[preStartDate] > mediumMa[preStartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (shortMa[preStartDate] < mediumMa[preStartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# 三均线策略
def strategy3(df, startDate, endDate, shortMA, mediumMA, longMA, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    # 收盘价
    close = df['Close']
    # 计算短期均线、中期均线和长期均线
    shortMa = close.rolling(shortMA).mean()
    mediumMa = close.rolling(mediumMA).mean()
    longMa = close.rolling(longMA).mean()

    # 取交易日期
    # 计算金叉 & 死叉
    goldenCross = (close > longMa) & (shortMa > mediumMa)
    judgeGoldenCross = ~goldenCross
    deathCross = ((close > longMa) & (shortMa < mediumMa)) | (close < longMa)
    judgeDeathCross = ~deathCross
    # 去重
    goldenCross = goldenCross & judgeGoldenCross.shift(1)
    deathCross = deathCross & judgeDeathCross.shift(1)

    # 买入日期 & 卖出日期
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 判断第一个交易日是否买入
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    if (close[preStartDate] > longMa[preStartDate]) and (shortMa[preStartDate] > mediumMa[preStartDate]) and (
            hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (close[preStartDate] < longMa[preStartDate]) or (
            (close[preStartDate] > longMa[preStartDate]) and (shortMa[preStartDate] < mediumMa[preStartDate])) and (
            hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# 双EMA策略
def strategy4(df, startDate, endDate, shortEMA, mediumEMA, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    # 收盘价
    close = df['Close']

    # 计算EMA
    shortEma = close.ewm(span=shortEMA, adjust=False).mean()
    mediumEma = close.ewm(span=mediumEMA, adjust=False).mean()

    # 计算金叉&死叉
    goldenCross = (shortEma > mediumEma) & (shortEma <= mediumEma).shift(1)
    deathCross = (shortEma < mediumEma) & (shortEma >= mediumEma).shift(1)

    # 买入日期 & 卖出日期
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 判断第一个交易日是否交易
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (shortEma[preStartDate] > mediumEma[preStartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (shortEma[preStartDate] < mediumEma[preStartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# MACD策略
def strategy5(df, startDate, endDate, DEA1, DEA2, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    # 收盘价
    close = df['Close']

    # DIF & DEA
    dif = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()  # DEA

    # 计算金叉 & 死叉、买入日期 & 卖出日期
    # goldenCross = ((dif > dea) & (dif <= dea).shift(1)) & (dea < DEA1)
    # deathCross = ((dif < dea)) & (dif >= dea).shift(1) & (dea > DEA2)
    judgeGoldenCross = (dif > dea) & (dea < DEA1)
    goldenCross = judgeGoldenCross & (~judgeGoldenCross).shift(1)
    judgeDeathCross = (dif < dea) & (dea > DEA2)
    deathCross = judgeDeathCross & (~judgeDeathCross).shift(1)

    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (dif[preStartDate] > dea[preStartDate]) and (dea[preStartDate] < DEA1) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (dif[preStartDate] < dea[preStartDate]) and (dea[preStartDate] > DEA2) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# KDJ
def strategy6a(df, startDate, endDate, buyD, sellD, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    # 要输出的df
    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    # 计算KDJ
    lowList = df['Low'].rolling(9).min()  # 计算low值9日移动最低
    highList = df['High'].rolling(9).max()  # 计算high值9日移动最高
    closeList = df['Close']  # 收盘价
    RSVList = (closeList - lowList) / (highList - lowList) * 100  # 计算RSV(未成熟随机值)
    k = RSVList.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算K值
    d = k.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算D值
    j = 3.0 * k - 2.0 * d  # 计算J值

    # 计算金叉 & 死叉
    judgeGoldenCross = (k > d) & (d < buyD)
    goldenCross = judgeGoldenCross & (~judgeGoldenCross).shift(1)
    judgeDeathCross = (k < d) & (d > sellD)
    deathCross = judgeDeathCross & (~judgeDeathCross).shift(1)

    # 计算买入日期 & 卖出日期
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (k[preStartDate] > d[preStartDate]) and (d[preStartDate] < buyD) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (k[preStartDate] < d[preStartDate]) and (d[preStartDate] > sellD) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign
    # 如果最后一个交易日为买,前一个交易日为买,将最后一个交易日置为0
    elif strategyDf.iloc[-1]['sign'] == buySign:
        judgeEndDate = strategyDf.dropna(subset=['sign'])
        if judgeEndDate.iloc[-2]['sign'] == buySign:
            strategyDf.loc[endDate, 'sign'] = startOrEndSign
    # 如果最后一个交易日为卖,前一个交易日为卖,将最后一个交易日置为0
    elif strategyDf.iloc[-1]['sign'] == sellSign:
        judgeEndDate = strategyDf.dropna(subset=['sign'])
        if judgeEndDate.iloc[-2]['sign'] == sellSign:
            strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# KDJ
def strategy6b(df, startDate, endDate, buyJ, sellJ, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    # 要输出的df
    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    # 计算KDJ
    lowList = df['Low'].rolling(9).min()  # 计算low值9日移动最低
    highList = df['High'].rolling(9).max()  # 计算high值9日移动最高
    closeList = df['Close']  # 收盘价
    RSVList = (closeList - lowList) / (highList - lowList) * 100  # 计算RSV(未成熟随机值)
    k = RSVList.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算K值
    d = k.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算D值
    j = 3.0 * k - 2.0 * d  # 计算J值
    preJ = j.shift(1)
    prePreJ = j.shift(2)

    # 计算金叉 & 死叉
    goldenCross = (j < buyJ) & (prePreJ > preJ) & (preJ < j)
    deathCross = (j > sellJ) & (prePreJ < preJ) & (preJ > j)

    # 计算买入日期 & 卖出日期
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的昨天
    prePreStartDate = Utils.getPreDate(df, preStartDate)  # 第一个交易日的前天
    prePrePreStartDate = Utils.getPreDate(df, prePreStartDate)  # 第一个交易日的大前天
    # 判断第一个交易日是否买入
    if (j[preStartDate] < buyJ) and (j[prePrePreStartDate] > j[prePreStartDate]) and (
            j[prePreStartDate] < j[preStartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (j[preStartDate] > sellJ) and (j[prePrePreStartDate] < j[prePreStartDate]) and (
            j[prePreStartDate] > j[preStartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign
    # 如果最后一个交易日为买,前一个交易日为买,将最后一个交易日置为0
    elif strategyDf.iloc[-1]['sign'] == buySign:
        judgeEndDate = strategyDf.dropna(subset=['sign'])
        if judgeEndDate.iloc[-2]['sign'] == buySign:
            strategyDf.loc[endDate, 'sign'] = startOrEndSign
    # 如果最后一个交易日为卖,前一个交易日为卖,将最后一个交易日置为0
    elif strategyDf.iloc[-1]['sign'] == sellSign:
        judgeEndDate = strategyDf.dropna(subset=['sign'])
        if judgeEndDate.iloc[-2]['sign'] == sellSign:
            strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# KDJ
def strategy6c(df, startDate, endDate, buyJ, sellJ, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    # 要输出的df
    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    # 计算KDJ
    lowList = df['Low'].rolling(9).min()  # 计算low值9日移动最低
    highList = df['High'].rolling(9).max()  # 计算high值9日移动最高
    closeList = df['Close']  # 收盘价
    RSVList = (closeList - lowList) / (highList - lowList) * 100  # 计算RSV(未成熟随机值)
    k = RSVList.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算K值
    d = k.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算D值
    j = 3.0 * k - 2.0 * d  # 计算J值
    prex1J = j.shift(1)
    prex2J = j.shift(2)
    prex3J = j.shift(3)

    # 计算金叉 & 死叉
    goldenCross = (j < buyJ) & (prex3J > prex2J) & (prex2J > prex1J) & (prex1J < j)
    deathCross = (j > sellJ) & (prex3J < prex2J) & (prex2J < prex1J) & (prex1J > j)

    # 计算买入日期 & 卖出日期
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    prex1StartDate = Utils.getPreDate(df, startDate)  # startDate-1
    prex2StartDate = Utils.getPreDate(df, prex1StartDate)  # startDate-2
    prex3StartDate = Utils.getPreDate(df, prex2StartDate)  # startDate-3
    prex4StartDate = Utils.getPreDate(df, prex3StartDate)  # startDate-4
    # 判断第一个交易日是否买入
    if (j[prex1StartDate] < buyJ) and (j[prex4StartDate] > j[prex3StartDate]) and (
            j[prex3StartDate] > j[prex2StartDate]) and (
            j[prex2StartDate] < j[prex1StartDate]) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (j[prex1StartDate] > sellJ) and (j[prex4StartDate] < j[prex3StartDate]) and (
            j[prex3StartDate] < j[prex2StartDate]) and (
            j[prex2StartDate] > j[prex1StartDate]) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign
    # 如果最后一个交易日为买,前一个交易日为买,将最后一个交易日置为0
    elif strategyDf.iloc[-1]['sign'] == buySign:
        judgeEndDate = strategyDf.dropna(subset=['sign'])
        if judgeEndDate.iloc[-2]['sign'] == buySign:
            strategyDf.loc[endDate, 'sign'] = startOrEndSign
    # 如果最后一个交易日为卖,前一个交易日为卖,将最后一个交易日置为0
    elif strategyDf.iloc[-1]['sign'] == sellSign:
        judgeEndDate = strategyDf.dropna(subset=['sign'])
        if judgeEndDate.iloc[-2]['sign'] == sellSign:
            strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    return strategyDf


# 交易
def trading(strategyDf, initBalance=1000000, initHold=0):
    startDate = strategyDf.iloc[0].name  # 获取第一个交易日
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
    dropList = []

    # 开始交易
    for i in range(0, len(tradingDf)):
        if signList[i] == buySign:
            # 已持有，不交易，待后续删除
            if hold != 0:
                dropList.append(tradingDf.iloc[i].name)
                continue
            beforeBalance = balance
            buynum = balance // (openList[i] * (1 + procedureRates))
            # 资金余额可以购买
            if buynum != 0:
                hold = holdList[i] = hold + buynum
                balance = balanceList[i] = balance - buynum * openList[i] * (1 + procedureRates)
                netAsset = netAssetList[i] = balance + buynum * openList[i]
        elif signList[i] == sellSign:
            # 已清仓，不交易，待后续删除
            if hold == 0:
                dropList.append(tradingDf.iloc[i].name)
                continue
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

    # 删除不交易的行
    tradingDf = tradingDf.drop(labels=dropList)

    return tradingDf


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


def getAllStrategy1(df, startDate, endDate, MARange=range(120, 241)):
    itAllStrategy = []
    for MA in MARange:
        strategyDf = strategy1(df, startDate, endDate, MA)
        tradingDf = trading(strategyDf)
        netAsset = tradingDf.iloc[-1]['netAsset']
        itAllStrategy.append([MA, netAsset])
        print('1:MA = {}, netAsset = {}'.format(MA, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['MA', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy2(df, startDate, endDate, shortMARange=range(1, 16), mediumMARange=range(20, 101)):
    itAllStrategy = []
    for shortMA in shortMARange:
        for mediumMA in mediumMARange:
            strategyDf = strategy2(df, startDate, endDate, shortMA, mediumMA)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([shortMA, mediumMA, netAsset])
            print('2:shortMA = {}, mediumMA = {}, netAsset = {}'.format(shortMA, mediumMA, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['shortMA', 'mediumMA', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy3(df, startDate, endDate, shortMARange=range(1, 9), mediumMARange=range(5, 22),
                    longMARange=range(120, 181)):
    itAllStrategy = []

    for shortMA in shortMARange:
        for mediumMA in mediumMARange:
            for longMA in longMARange:
                # 短期均线一定小于中期均线和长期均线
                # 中期均线一定小于长期均线
                if (shortMA >= mediumMA) or (shortMA >= longMA) or (mediumMA >= longMA):
                    continue
                strategyDf = strategy3(df, startDate, endDate, shortMA, mediumMA, longMA)
                tradingDf = trading(strategyDf)
                netAsset = tradingDf.iloc[-1]['netAsset']
                itAllStrategy.append([int(shortMA), int(mediumMA), int(longMA), netAsset])
                print('3:shortMA = {}, mediumMA = {}, longMA = {}, netAsset = {}'.format(shortMA, mediumMA, longMA,
                                                                                         netAsset), end='\r')
    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['shortMA', 'mediumMA', 'longMA', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy4(df, startDate, endDate, shortEMARange=range(1, 16), mediumEMARange=range(20, 101)):
    itAllStrategy = []

    for shortEMA in shortEMARange:
        for mediumEMA in mediumEMARange:
            strategyDf = strategy4(df, startDate, endDate, shortEMA, mediumEMA)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([shortEMA, mediumEMA, netAsset])
            print('4:shortEMA = {}, mediumEMA={}, netAsset = {}'.format(shortEMA, mediumEMA, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['shortEMA', 'mediumEMA', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy5(df, startDate, endDate, DEA1Range=range(-100, 101), DEA2Range=range(-100, 101)):
    itAllStrategy = []

    for DEA2 in DEA2Range:
        for DEA1 in DEA1Range:
            strategyDf = strategy5(df, startDate, endDate, DEA1, DEA2)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([DEA2, DEA1, netAsset])
            print('5:DEA1={}, DEA2={}, netAsset={}'.format(DEA1, DEA2, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['DEA2', 'DEA1', 'netAsset'])

    return itAllStrategyDf


def getAllStrategy6a(df, startDate, endDate, buyDRange=range(10, 91), sellDRange=range(20, 101)):
    itAllStrategy = []

    for sellD in sellDRange:
        for buyD in buyDRange:
            strategyDf = strategy6a(df, startDate, endDate, buyD, sellD)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([sellD, buyD, netAsset])
            print('6a:sellD={}, buyD={}, netAsset={}'.format(sellD, buyD, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['sellD', 'buyD', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy6b(df, startDate, endDate, buyJRange=range(10, 91), sellJRange=range(30, 111)):
    itAllStrategy = []

    for sellJ in sellJRange:
        for buyJ in buyJRange:
            strategyDf = strategy6b(df, startDate, endDate, buyJ, sellJ)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([sellJ, buyJ, netAsset])
            print('6b:sellJ={}, buyJ={}, netAsset={}'.format(sellJ, buyJ, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['sellJ', 'buyJ', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy6c(df, startDate, endDate, buyJRange=range(10, 91), sellJRange=range(30, 111)):
    itAllStrategy = []

    for sellJ in sellJRange:
        for buyJ in buyJRange:
            strategyDf = strategy6c(df, startDate, endDate, buyJ, sellJ)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([sellJ, buyJ, netAsset])
            print('6c:sellJ={}, buyJ={}, netAsset={}'.format(sellJ, buyJ, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['sellJ', 'buyJ', 'netAsset'])
    return itAllStrategyDf


def getBestStrategy1(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestMA = itAllStrategyDf.loc[bestID, 'MA']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestMA, bestNetAsset


def getBestStrategy2(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestShortMA = itAllStrategyDf.loc[bestID, 'shortMA']
    bestMediumMA = itAllStrategyDf.loc[bestID, 'mediumMA']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestShortMA, bestMediumMA, bestNetAsset


def getBestStrategy3(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestShortMA = itAllStrategyDf.loc[bestID, 'shortMA']
    bestMediumMA = itAllStrategyDf.loc[bestID, 'mediumMA']
    bestLongMA = itAllStrategyDf.loc[bestID, 'longMA']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestShortMA, bestMediumMA, bestLongMA, bestNetAsset


def getBestStrategy4(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestShortEMA = itAllStrategyDf.loc[bestID, 'shortEMA']
    bestMediumEMA = itAllStrategyDf.loc[bestID, 'mediumEMA']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']

    return bestShortEMA, bestMediumEMA, bestNetAsset


def getBestStrategy5(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestDEA1 = itAllStrategyDf.loc[bestID, 'DEA1']
    bestDEA2 = itAllStrategyDf.loc[bestID, 'DEA2']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestDEA1, bestDEA2, bestNetAsset


def getBestStrategy6b(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestBuyJ = itAllStrategyDf.loc[bestID, 'buyJ']
    bestSellJ = itAllStrategyDf.loc[bestID, 'sellJ']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestBuyJ, bestSellJ, bestNetAsset


def getBestStrategy6a(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestBuyD = itAllStrategyDf.loc[bestID, 'buyD']
    bestSellD = itAllStrategyDf.loc[bestID, 'sellD']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestBuyD, bestSellD, bestNetAsset


def getBestStrategy6c(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestBuyJ = itAllStrategyDf.loc[bestID, 'buyJ']
    bestSellJ = itAllStrategyDf.loc[bestID, 'sellJ']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestBuyJ, bestSellJ, bestNetAsset


def getTotalRate(initBalance, netAsset):
    totalRate = (netAsset - initBalance) / initBalance
    return totalRate


def getCompoundRate(totalRate, startDate, endDate):
    # # 将开始日期和结束日期转换为时间戳
    # first = time.mktime((time.strptime(startDate, "%Y-%m-%d")))
    # last = time.mktime((time.strptime(endDate, "%Y-%m-%d")))
    #
    # # 计算交易区间的天数
    # days = (last - first) / (24 * 3600) + 1

    # 计算交易区间的天数
    days = Utils.getDayNum(startDate, endDate)

    # 计算：年均收益率复利 <- 总收益率
    compoundRate = (totalRate + 1) ** (365.0 / days) - 1

    return compoundRate


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


def slidingWindowTrading(df, backtestStartDate, backtestEndDate, sampleYear, initBalance=1000000):
    '''
    根据样本内年份，寻找最佳指标，并用到下一年进行回测
    '''
    balance = initBalance  # 现金余额
    hold = 0

    # 计算日期数据
    backtestStartYear = int(backtestStartDate[:4])  # 回测开始年份
    backtestEndYear = int(backtestEndDate[:4])  # 回测结束年份
    backtestYear = backtestEndYear - backtestStartYear + 1
    sampleStartYear = backtestStartYear - sampleYear  # 样本开始年份
    sampleEndYear = backtestStartYear - 1  # 样本结束年份

    # 计算涉及年份的第一个交易日和最后一个交易日
    yearDf = pd.DataFrame(columns=['startDate', 'endDate'])
    for year in range(sampleStartYear, backtestEndYear + 1):
        yearDf.loc[year] = [Utils.getFirstDate(df, year), Utils.getLastDate(df, year)]

    bestDf = pd.DataFrame(
        columns=['样本内数据年份数', '第iyear窗口', '最佳策略', '最佳样本内净资产',
                 'bestMA1', 'bestNetAsset1',
                 'bestShortMA2', 'bestMediumMA2', 'bestNetAsset2',
                 'bestShortMA3', 'bestMediumMA3', 'bestLongMA3', 'bestNetAsset3',
                 'bestShortEMA4', 'bestMediumEMA4', 'bestNetAsset4',
                 'bestDEA15', 'bestDEA25', 'bestNetAsset5',
                 'bestBuyD6a', 'bestSellD6a', 'bestNetAsset6a',
                 'bestBuyJ6b', 'bestSellJ6b', 'bestNetAsset6b',
                 'bestBuyJ6c', 'bestSellJ6c', 'bestNetAsset6c',
                 ])
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

        # 找最佳参数
        bestStrategy = '1'
        bestNetAsset = -1
        # 策略1
        sampleAllStrategyDf1 = getAllStrategy1(df, sampleStartDate, sampleEndDate)
        bestMA1, bestNetAsset1 = getBestStrategy1(sampleAllStrategyDf1)
        if bestNetAsset1 > bestNetAsset:
            bestStrategy = '1'
            bestNetAsset = bestNetAsset1
        # 策略2
        sampleAllStrategyDf2 = getAllStrategy2(df, sampleStartDate, sampleEndDate)
        bestShortMA2, bestMediumMA2, bestNetAsset2 = getBestStrategy2(sampleAllStrategyDf2)
        if bestNetAsset2 > bestNetAsset:
            bestStrategy = '2'
            bestNetAsset = bestNetAsset2
        # 策略3
        sampleAllStrategyDf3 = getAllStrategy3(df, sampleStartDate, sampleEndDate)
        bestShortMA3, bestMediumMA3, bestLongMA3, bestNetAsset3 = getBestStrategy3(sampleAllStrategyDf3)
        if bestNetAsset3 > bestNetAsset:
            bestStrategy = '3'
            bestNetAsset = bestNetAsset3
        # 策略4
        sampleAllStrategyDf4 = getAllStrategy4(df, sampleStartDate, sampleEndDate)
        bestShortEMA4, bestMediumEMA4, bestNetAsset4 = getBestStrategy4(sampleAllStrategyDf4)
        if bestNetAsset4 > bestNetAsset:
            bestStrategy = '4'
            bestNetAsset = bestNetAsset4
        # 策略5
        sampleAllStrategyDf5 = getAllStrategy5(df, sampleStartDate, sampleEndDate)
        bestDEA15, bestDEA25, bestNetAsset5 = getBestStrategy5(sampleAllStrategyDf5)
        if bestNetAsset5 > bestNetAsset:
            bestStrategy = '5'
            bestNetAsset = bestNetAsset5
        # 策略6a
        sampleAllStrategyDf6a = getAllStrategy6a(df, sampleStartDate, sampleEndDate)
        bestBuyD6a, bestSellD6a, bestNetAsset6a = getBestStrategy6a(sampleAllStrategyDf6a)
        if bestNetAsset6a > bestNetAsset:
            bestStrategy = '6a'
            bestNetAsset = bestNetAsset6a
        # 策略6b
        sampleAllStrategyDf6b = getAllStrategy6b(df, sampleStartDate, sampleEndDate)
        bestBuyJ6b, bestSellJ6b, bestNetAsset6b = getBestStrategy6b(sampleAllStrategyDf6b)
        if bestNetAsset6b > bestNetAsset:
            bestStrategy = '6b'
            bestNetAsset = bestNetAsset6b
        # 策略6c
        sampleAllStrategyDf6c = getAllStrategy6c(df, sampleStartDate, sampleEndDate)
        bestBuyJ6c, bestSellJ6c, bestNetAsset6c = getBestStrategy6c(sampleAllStrategyDf6c)
        if bestNetAsset6c > bestNetAsset:
            bestStrategy = '6c'
            bestNetAsset = bestNetAsset6c

        # 保存
        bestDf.loc[iyear] = [sampleYear, iyear, bestStrategy, bestNetAsset,
                             bestMA1, bestNetAsset1,
                             bestShortMA2, bestMediumMA2, bestNetAsset2,
                             bestShortMA3, bestMediumMA3, bestLongMA3, bestNetAsset3,
                             bestShortEMA4, bestMediumEMA4, bestNetAsset4,
                             bestDEA15, bestDEA25, bestNetAsset5,
                             bestBuyD6a, bestSellD6a, bestNetAsset6a,
                             bestBuyJ6b, bestSellJ6b, bestNetAsset6b,
                             bestBuyJ6c, bestSellJ6c, bestNetAsset6c,
                             ]

        # 将最佳MA放入滑动窗口进行回测
        if bestStrategy == '1':
            slidingWindowStrategyDf = strategy1(df, slidingWindowStartDate, slidingWindowEndDate,
                                                bestMA1,
                                                hold=hold)
        elif bestStrategy == '2':
            slidingWindowStrategyDf = strategy2(df, slidingWindowStartDate, slidingWindowEndDate,
                                                bestShortMA2, bestMediumMA2,
                                                hold=hold)
        elif bestStrategy == '3':
            slidingWindowStrategyDf = strategy3(df, slidingWindowStartDate, slidingWindowEndDate,
                                                bestShortMA3, bestMediumMA3, bestLongMA3,
                                                hold=hold)
        elif bestStrategy == '4':
            slidingWindowStrategyDf = strategy4(df, slidingWindowStartDate, slidingWindowEndDate,
                                                bestShortEMA4, bestMediumEMA4,
                                                hold=hold)
        elif bestStrategy == '5':
            slidingWindowStrategyDf = strategy5(df, slidingWindowStartDate, slidingWindowEndDate,
                                                bestDEA15, bestDEA15,
                                                hold=hold)
        elif bestStrategy == '6a':
            slidingWindowStrategyDf = strategy6a(df, slidingWindowStartDate, slidingWindowEndDate,
                                                 bestBuyD6a, bestSellD6a,
                                                 hold=hold)
        elif bestStrategy == '6b':
            slidingWindowStrategyDf = strategy6b(df, slidingWindowStartDate, slidingWindowEndDate,
                                                 bestBuyJ6b, bestSellJ6b,
                                                 hold=hold)
        elif bestStrategy == '6c':
            slidingWindowStrategyDf = strategy6c(df, slidingWindowStartDate, slidingWindowEndDate,
                                                 bestBuyJ6c, bestSellJ6c,
                                                 hold=hold)

        newBacktestTradingDf = trading(slidingWindowStrategyDf, balance, hold)
        backtestTradingDf = pd.concat([backtestTradingDf, newBacktestTradingDf])

        balance = backtestTradingDf.iloc[-1]['balance']
        hold = backtestTradingDf.iloc[-1]['hold']
        # netAsset = backtestTradingDf.iloc[-1]['netAsset']

    # 扩充最佳组合明细
    backtestNewTradingDf = getNewTradingDf(df, backtestTradingDf, backtestStartDate, backtestEndDate)

    # 计算净资产 & 总收益率 & 年复利 & 最大回撤率
    backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
    backtestTotalRate = getTotalRate(initBalance, backtestNetAsset)
    backtestCompoundRate = getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)
    backtestMaxDrawDown = getMaxDrawDown(backtestNewTradingDf)
    backtestYearTotalRateDf = getYearTotalRateDf(backtestNewTradingDf, backtestStartDate, backtestEndDate)
    backtestSharpeRatio = getSharpRatio(backtestYearTotalRateDf)
    resultSr = pd.Series([sampleYear, backtestNetAsset, backtestTotalRate, backtestCompoundRate, backtestMaxDrawDown,
                          backtestSharpeRatio],
                         index=['样本内数据年份数', '样本外净资产', '总收益率', '年复利', '最大回撤率', '夏普率'])

    return bestDf, backtestTradingDf, resultSr, backtestYearTotalRateDf
