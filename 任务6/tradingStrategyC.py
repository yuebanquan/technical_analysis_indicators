import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import Utils


def strategy(df, startDate, endDate, buyJ, sellJ, hold=0, debug=False):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    # 要输出的df
    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    j = df['J']
    prex1J = j.shift(1)
    prex2J = j.shift(2)
    prex3J = j.shift(3)

    # 显示J
    if debug:
        strategyDf['j'] = j
        strategyDf['preJ'] = prex1J
        strategyDf['prePreJ'] = prex2J
        strategyDf['prePrePreJ'] = prex3J

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
            # 已持有且不是最后一日，不交易，待后续删除
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


def getAllStrategy(df, startDate, endDate, buyJRange, sellJRange):
    itAllStrategy = []

    for sellJ in sellJRange:
        for buyJ in buyJRange:
            strategyDf = strategy(df, startDate, endDate, buyJ, sellJ)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([sellJ, buyJ, netAsset])
            print('sellJ={}, buyJ={}, netAsset={}'.format(sellJ, buyJ, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['sellJ', 'buyJ', 'netAsset'])
    return itAllStrategyDf


def getBestStrategy(itAllStrategyDf):
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


def slidingWindowTrading(df, backtestStartDate, backtestEndDate, sampleYear, buyJRange, sellJRange,
                         initBalance=1000000, debug=False):
    '''
    根据样本内年份，寻找最佳指标，并用到下一年进行回测
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

    bestDf = pd.DataFrame(
        columns=['样本内数据年份数', '第iyear窗口', '最佳J1', '最佳J2', '样本内净资产'])
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
        sampleAllStrategyDf = getAllStrategy(df, sampleStartDate, sampleEndDate, buyJRange, sellJRange)
        """
        debug
        """
        if debug == True:
            file = r"./result/" + str(sampleYear) + "/" + "iyear_" + str(iyear) + ".csv"
            sampleAllStrategyDf.to_csv(file)

        bestBuyD, bestSellD, bestNetAsset = getBestStrategy(sampleAllStrategyDf)
        bestDf.loc[iyear] = [sampleYear, iyear, bestBuyD, bestSellD, bestNetAsset]

        # 将最佳MA放入滑动窗口进行回测
        slidingWindowStrategyDf = strategy(df, slidingWindowStartDate, slidingWindowEndDate, bestBuyD, bestSellD,
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

    return bestDf, backtestTradingDf, resultSr
