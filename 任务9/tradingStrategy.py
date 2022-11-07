import numpy as np
import pandas as pd
import Utils
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import time
import datetime
import dateutil.relativedelta


# 双均线策略
def strategy(df, startDate, endDate, shortMA, mediumMA, hold=0):
    # 交易信号
    buySign = 1  # 买入信号
    sellSign = -1  # 卖出信号
    startOrEndSign = 0  # 交易上下限

    strategyDf = df.copy()[['Open', 'Close']]  # 策略DataFrame
    strategyDf = strategyDf[startDate:endDate]

    close = df['Close']
    shortMa = close.rolling(shortMA).mean()
    mediumMa = close.rolling(mediumMA).mean()

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


def getAllStrategy(df, startDate, endDate, shortMARange, mediumMARange):
    itAllStrategy = []
    for shortMA in shortMARange:
        for mediumMA in mediumMARange:
            strategyDf = strategy(df, startDate, endDate, shortMA, mediumMA)
            tradingDf = trading(strategyDf)
            netAsset = tradingDf.iloc[-1]['netAsset']
            itAllStrategy.append([shortMA, mediumMA, netAsset])

            print('shortMA = {}, mediumMA = {}, netAsset = {}'.format(shortMA, mediumMA, netAsset), end='\r')

    itAllStrategyDf = pd.DataFrame(itAllStrategy, columns=['shortMA', 'mediumMA', 'netAsset'])
    return itAllStrategyDf


def getBestStrategy(itAllStrategyDf):
    bestID = itAllStrategyDf['netAsset'].idxmax()
    bestShortMA = itAllStrategyDf.loc[bestID, 'shortMA']
    bestMediumMA = itAllStrategyDf.loc[bestID, 'mediumMA']
    bestNetAsset = itAllStrategyDf.loc[bestID, 'netAsset']
    return bestShortMA, bestMediumMA, bestNetAsset


def getTotalRate(initBalance, netAsset):
    totalRate = (netAsset - initBalance) / initBalance
    return totalRate


def getCompoundRate(totalRate, startDate, endDate):
    # 将开始日期和结束日期转换为时间戳
    first = time.mktime(startDate.timetuple())
    last = time.mktime(endDate.timetuple())

    # 计算交易区间的天数
    days = (last - first) / (24 * 3600) + 1

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


def slidingWindowTrading(df,
                         backtestStartDate, stepMonth,
                         backtestEndDate, sampleDataSize,
                         shortMARange, mediumMARange,
                         initBalance
                         ):
    ############## 计算每个窗口的样本外开始时间和结束时间 ##############
    slidingWindowBacktestStartDateList = []  # List, 存每个窗口样本外开始日期
    slidingWindowBacktestEndDateList = []  # List, 存每个窗口样本外结束日期

    delta = backtestStartDate  # 循环控制条件
    while (delta < backtestEndDate):  # 以相应步长遍历样本外区间
        # 计算窗口样本外开始日期
        startDate = df.loc[delta.strftime('%Y-%m')].index[0]  # 该窗口的样本外开始日期:这个月的第一个交易日
        slidingWindowBacktestStartDateList.append(startDate)  # 加入List中

        # 计算窗口样本外结束日期
        try:
            endDate = \
                df.loc[(delta + dateutil.relativedelta.relativedelta(months=stepMonth - 1)).strftime('%Y-%m')].tail(
                    1).index[0]  # 该窗口的样本外结束日期:(开始日期 + 步长 - 1)的月份最后一天
            slidingWindowBacktestEndDateList.append(endDate)  # 加入List中
        except Exception as e:
            # 抛出异常, 说明最后一个窗口不满步长, 该窗口样本内外结束日期为样本外结束日期
            slidingWindowBacktestEndDateList.append(backtestEndDate)

        delta = delta + dateutil.relativedelta.relativedelta(months=stepMonth)  # 循环控制条件增加相应步长

    ############## 每个滑动窗口的最佳参数组合 ##############
    bestDf = pd.DataFrame(
        data={'样本内数据年份数': sampleDataSize, '步长/月': stepMonth,
              '样本外开始': slidingWindowBacktestStartDateList, '样本外结束': slidingWindowBacktestEndDateList},
        columns=['样本内数据年份数', '步长/月',
                 '样本内开始', '样本内结束',
                 '样本外开始', '样本外结束',
                 '最佳短期均线', '最佳中期均线', '样本内净资产'])

    ############## 计算每个窗口的样本内开始时间和结束时间 ##############
    bestDf['样本内开始'] = bestDf['样本外开始'].apply(
        lambda x: df.loc[(x - dateutil.relativedelta.relativedelta(years=sampleDataSize)).strftime('%Y-%m')].index[0]
    )  # 样本内开始 = (样本外开始 - 步长)那个月的第一个交易日

    bestDf['样本内结束'] = bestDf['样本外开始'].apply(
        lambda x: df.loc[(x - dateutil.relativedelta.relativedelta(months=1)).strftime('%Y-%m')].tail(1).index[
            0]
    )  # 样本内结束 = 样本外开始那个月的上一个月的最后一个交易日

    ############## 计算每个窗口的最佳参数并回测 ##############
    # 将bestDf向量化
    slidingWindowSampleStartDateList = bestDf['样本内开始'].values
    slidingWindowSampleEndDateList = bestDf['样本内结束'].values
    slidingWindowBacktestStartDateList = bestDf['样本外开始'].values
    slidingWindowBacktestEndDateList = bestDf['样本外结束'].values
    bestShortMAList = bestDf['最佳短期均线'].values
    bestMediumMAList = bestDf['最佳中期均线'].values
    bestNetAssetList = bestDf['样本内净资产'].values

    # 使用最佳参数回测交易明细
    backtestTradingDf = pd.DataFrame(
        columns=['Open', 'Close', 'sign', 'hold', 'balance', 'netAsset', 'profit'])

    # 遍历bestDf, 计算每个窗口的最佳参数组合
    balance = initBalance  # 样本外区间进行回测时持有的现金
    hold = 0  # 样本外区间进行回测时持有的证券数量
    for i in range(len(bestNetAssetList)):
        # 进度
        print(str(i + 1) + '/' + str(len(bestNetAssetList)))

        ############样本内区间############
        # 样本内区间, 计算最佳参数
        iSampleStartDate = slidingWindowSampleStartDateList[i]  # 该窗口样本内开始时间
        iSampleEndDate = slidingWindowSampleEndDateList[i]  # 该窗口样本内结束时间

        itAllStrategyDf = getAllStrategy(df, iSampleStartDate, iSampleEndDate, shortMARange,
                                         mediumMARange)  # 计算该窗口所有参数
        bestShortMA, bestMediumMA, bestNetAsset = getBestStrategy(itAllStrategyDf)  # 找最佳参数

        # 写入最佳参数
        bestShortMAList[i] = bestShortMA
        bestMediumMAList[i] = bestMediumMA
        bestNetAssetList[i] = bestNetAsset

        ############样本外区间############
        # 使用最佳参数在该窗口进行回测
        iBacktestStartDate = slidingWindowBacktestStartDateList[i]  # 该窗口样本外开始时间
        iBacktestEndDate = slidingWindowBacktestEndDateList[i]  # 该窗口样本外结束时间

        backtestStrategyDf = strategy(df,
                                      iBacktestStartDate, iBacktestEndDate,
                                      bestShortMA, bestMediumMA,
                                      hold)  # 该窗口买卖标志位
        newBacktestTradingDf = trading(backtestStrategyDf, balance, hold)  # 该窗口交易明细

        balance = newBacktestTradingDf.iloc[-1]['balance']  # 更新现金
        hold = newBacktestTradingDf.iloc[-1]['hold']  # 更新持有证券数量

        backtestTradingDf = pd.concat([backtestTradingDf, newBacktestTradingDf])  # 将该窗口交易明细合并进回测交易明细中

    ############## 计算回测的净资产、复利 ##############
    backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
    backtestTotalRate = getTotalRate(initBalance, backtestNetAsset)
    backtestCompoundRate = getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)
    resultSr = pd.Series([sampleDataSize, stepMonth, backtestNetAsset, backtestCompoundRate],
                         index=['样本内数据年份数', '步长/月', '样本外净资产', '年均收益率复利'])

    return bestDf, backtestTradingDf, resultSr
