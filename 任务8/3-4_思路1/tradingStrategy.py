import numpy as np
import pandas as pd
import Utils
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


# 计算EMA
def getEMADf(df, emaRange):
    # 计算EMA:1-100
    emaDf = pd.DataFrame(np.full((len(df), 101), np.nan), index=df.index).drop(columns=0)  # ema表

    for ema in emaRange:
        emaDf[ema] = df.Close.ewm(span=ema, adjust=False).mean()
    return emaDf


# 计算MACD
def getMACDDf(df):
    macdDf = pd.DataFrame(columns=['dif', 'dea'], index=df.index)  # MACD表

    close = df.Close  # 收盘价
    macdDf['dif'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()  # DIF
    macdDf['dea'] = macdDf['dif'].ewm(span=9, adjust=False).mean()  # DEA

    return macdDf


# EMA + MACD策略
def strategy(df, emaDf, macdDf, startDate, endDate, shortEMA, mediumEMA, DEA1, DEA2, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    # 拷贝策略DataFrame
    strategyDf = df.copy()[['Open', 'Close']]
    strategyDf = strategyDf[startDate:endDate]

    # shortEma & mediumEma & dif & dea
    shortEma = emaDf[shortEMA]
    mediumEma = emaDf[mediumEMA]
    dif = macdDf['dif']
    dea = macdDf['dea']

    # 计算金叉 & 死叉
    judgeGoldenCross = (shortEma > mediumEma) & (dif > dea) & (dea < DEA1)
    judgeDeathCross = (shortEma < mediumEma) & (dif < dea) & (dea > DEA2)
    goldenCross = judgeGoldenCross & (~judgeGoldenCross).shift(1)
    deathCross = judgeDeathCross & (~judgeDeathCross).shift(1)

    # # 计算金叉 & 死叉
    # goldenCross = (shortEma > mediumEma) & (dif > dea) & (dea < DEA1)
    # deathCross = (shortEma < mediumEma) & (dif < dea) & (dea > DEA2)

    # 计算买入日期 & 卖出日期
    buyDate = goldenCross.shift(1)
    sellDate = deathCross.shift(1)

    # 标记买卖标志位(除第一个交易日和最后一个交易日)
    strategyDf.loc[buyDate == True, 'sign'] = buySign
    strategyDf.loc[sellDate == True, 'sign'] = sellSign

    # 标记第一个交易日的买卖标志位
    preStartDate = Utils.getPreDate(df, startDate)  # 第一个交易日的前一个交易日
    # 判断第一个交易日是否买入
    if (shortEma[preStartDate] > mediumEma[preStartDate]) and (dif[preStartDate] > dea[preStartDate]) and (
            dea[preStartDate] < DEA1) and (hold == 0):
        strategyDf.loc[startDate, 'sign'] = buySign
    # 判断第一个交易日是否卖出
    elif (shortEma[preStartDate] < mediumEma[preStartDate]) and (dif[preStartDate] < dea[preStartDate]) and (
            dea[preStartDate] > DEA2) and (hold != 0):
        strategyDf.loc[startDate, 'sign'] = sellSign
    else:
        strategyDf.loc[startDate, 'sign'] = startOrEndSign

    # 如果最后一个交易日不交易，买卖信号置为0
    if np.isnan(strategyDf.loc[endDate, 'sign']):
        strategyDf.loc[endDate, 'sign'] = startOrEndSign

    # # 风控: 止盈 & 止损
    # strategyDf['test'] = np.nan
    # testList = strategyDf.test.values
    # closeList = strategyDf.Close.values
    # signList = strategyDf.sign.values
    # stopProfitPoint = -0.05
    # partCloseMax = 0  # 局部收盘价最大值: 每次买入刷新
    # partHold = 0  # 持有标志符: 持有:1, 不持有:0
    # for i in range(len(strategyDf)):
    #     # 买入, 刷新局部收盘价最大值 & 持有标志符
    #     if signList[i] == buySign:
    #         partCloseMax = closeList[i]
    #         partHold = 1
    #
    #     # 不持有, 跳过, 使得循环只计算持有的时候
    #     if partHold == 0:
    #         continue
    #
    #     # 如果当前收盘价高于局部收盘价最大值, 更新局部收盘价最大值
    #     if closeList[i] > partCloseMax:
    #         partCloseMax = closeList[i]
    #
    #     partDrowDown = (closeList[i] - partCloseMax) / partCloseMax  # 计算局部回撤率(回撤时为负数)
    #
    #     # 局部回撤率大于止盈点时, 卖出: 更新持有标志符
    #     if partDrowDown <= stopProfitPoint:
    #         signList[i] = sellSign
    #         partHold = 0
    #         testList = 1
    #     # 卖出, 更新持有标志符
    #     elif signList[i] == sellSign:
    #         partHold = 0

    # 除去除交易上下限外不交易的日期
    strategyDf = strategyDf.dropna(subset=['sign'])

    # 防止重复买入卖出
    strategyDf = strategyDf.loc[(strategyDf.sign != strategyDf.sign.shift(1)) | (strategyDf.index == endDate)]

    # 防止第一个交易日没动作,后面又卖的情况, 删除卖的那一行
    if (strategyDf.iloc[0]['sign'] == startOrEndSign) and (strategyDf.iloc[1]['sign'] == sellSign):
        strategyDf = strategyDf.drop(index=strategyDf.index[[1]])

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
        if signList[i] == buySign and hold == 0:
            beforeBalance = balance
            buynum = balance // (openList[i] * (1 + procedureRates))
            # 资金余额可以购买
            if buynum != 0:
                hold = holdList[i] = hold + buynum
                balance = balanceList[i] = balance - buynum * openList[i] * (1 + procedureRates)
                netAsset = netAssetList[i] = balance + buynum * openList[i]
        elif signList[i] == sellSign and hold != 0:
            balance = balanceList[i] = balance + hold * openList[i] * (1 - procedureRates)
            netAsset = netAssetList[i] = balance
            profitList[i] = balance - beforeBalance
            hold = holdList[i] = 0
        elif signList[i] == startOrEndSign:
            holdList[i] = hold
            balanceList[i] = balance
            netAssetList[i] = balance + hold * closeList[i]
            profitList[i] = balance - beforeBalance

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


def getAllStrategy1(df, emaDf, macdDf, startDate, endDate, shortEMARange, meduimEMARange, DEA1Range, DEA2Range):
    itAllStrategy = []

    preBestNetAsset = -1000000000
    bestNetAsset = -1
    granularity = 100000

    for shortEMA in shortEMARange:
        for meduimEMA in meduimEMARange:
            if shortEMA >= meduimEMA:
                continue
            for DEA2 in DEA2Range:
                for DEA1 in DEA1Range:
                    strategyDf = strategy(df, emaDf, macdDf, startDate, endDate, shortEMA, meduimEMA, DEA1, DEA2)
                    tradingDf = trading(strategyDf)
                    netAsset = tradingDf.iloc[-1]['netAsset']
                    itAllStrategy.append([shortEMA, meduimEMA, DEA1, DEA2, netAsset])
                    print('shortEMA = {}, meduimEMA = {}, DEA2={}, DEA1={}, netAsset = {}'.format(shortEMA, meduimEMA,
                                                                                                  DEA2, DEA1, netAsset),
                          end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['shortEMA', 'mediumEMA', 'DEA1', 'DEA2', 'netAsset'])
    return itAllStrategyDf


def getAllStrategy(df, emaDf, macdDf, startDate, endDate, shortEMARange, meduimEMARange, DEA1Range, DEA2Range):
    itAllStrategy = []

    for shortEMA in shortEMARange:
        for meduimEMA in meduimEMARange:
            if shortEMA >= meduimEMA:
                continue
            for DEA2 in DEA2Range:
                for DEA1 in DEA1Range:
                    strategyDf = strategy(df, emaDf, macdDf, startDate, endDate, shortEMA, meduimEMA, DEA1, DEA2)
                    tradingDf = trading(strategyDf)
                    netAsset = tradingDf.iloc[-1]['netAsset']
                    itAllStrategy.append([shortEMA, meduimEMA, DEA1, DEA2, netAsset])
                    print('shortEMA = {}, meduimEMA = {}, DEA2={}, DEA1={}, netAsset = {}'.format(shortEMA, meduimEMA,
                                                                                                  DEA2, DEA1, netAsset),
                          end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['shortEMA', 'mediumEMA', 'DEA1', 'DEA2', 'netAsset'])
    return itAllStrategyDf


def getBestStrategy(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestShortEMA = itAllStrategyDf.loc[bestID, 'shortEMA']
    bestMediumEMA = itAllStrategyDf.loc[bestID, 'mediumEMA']
    bestDEA1 = itAllStrategyDf.loc[bestID, 'DEA1']
    bestDEA2 = itAllStrategyDf.loc[bestID, 'DEA2']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestShortEMA, bestMediumEMA, bestDEA1, bestDEA2, bestNetAsset


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


def getFR(newTradingDf, frFile, closeStd, netAssetStd):
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


def slidingWindowTrading(df, emaDf, macdDf,
                         backtestStartDate, backtestEndDate, sampleYear,
                         shortEMARange, meduimEMARange, DEA1Range, DEA2Range,
                         initBalance):
    '''
    根据样本内年份，寻找最佳指标，并用到下一年进行回测
    '''
    balance = initBalance  # 现金余额
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

    bestDf = pd.DataFrame(columns=['样本内数据年份数', '第iyear窗口',
                                   'bestShortEMA', 'bestMeduimEMA', 'bestDEA1', 'bestDEA2',
                                   '样本内净资产'],
                          index=[iyear for iyear in range(0, backtestYear)])
    backtestTradingDf = pd.DataFrame(columns=['Open', 'Close', 'sign', 'hold', 'balance', 'netAsset', 'profit'])

    for iyear in range(0, backtestYear):
        # # 跳过
        # if iyear != 7:
        #     continue

        sampleStartDate = yearDf.loc[sampleStartYear + iyear, 'startDate']
        sampleEndDate = yearDf.loc[sampleEndYear + iyear, 'endDate']
        slidingWindowStartDate = yearDf.loc[backtestStartYear + iyear, 'startDate']
        slidingWindowEndDate = yearDf.loc[backtestStartYear + iyear, 'endDate']
        print(slidingWindowStartDate + " to " + slidingWindowEndDate)

        # # 找最佳参数
        # sampleAllStrategyDf = getAllStrategy(df, emaDf, macdDf,
        #                                      sampleStartDate, sampleEndDate,
        #                                      shortEMARange, meduimEMARange, DEA1Range, DEA2Range)
        # bestShortEMA, bestMediumEMA, bestDEA1, bestDEA2, bestNetAsset = getBestStrategy(sampleAllStrategyDf)
        #
        # bestDf.loc[iyear, :] = [sampleYear, iyear, bestShortEMA, bestMediumEMA, bestDEA1, bestDEA2, bestNetAsset]

        bestDf = pd.read_csv(r"./result/2_1_最佳参数组合交易明细.csv")

        bestShortEMA = bestDf.loc[iyear, 'bestShortEMA']
        bestMeduimEMA = bestDf.loc[iyear, 'bestMeduimEMA']
        bestDEA1 = bestDf.loc[iyear, 'bestDEA1']
        bestDEA2 = bestDf.loc[iyear, 'bestDEA2']

        # 将最佳参数放入滑动窗口进行回测
        slidingWindowStrategyDf = strategy(df, emaDf, macdDf,
                                           slidingWindowStartDate, slidingWindowEndDate,
                                           bestShortEMA, bestMeduimEMA, bestDEA1, bestDEA2,
                                           hold=hold)
        newBacktestTradingDf = trading(slidingWindowStrategyDf, balance, hold)
        backtestTradingDf = pd.concat([backtestTradingDf, newBacktestTradingDf])

        balance = backtestTradingDf.iloc[-1]['balance']
        hold = backtestTradingDf.iloc[-1]['hold']

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

    return bestDf, backtestTradingDf, backtestYearTotalRateDf, resultSr

    # return bestDf
