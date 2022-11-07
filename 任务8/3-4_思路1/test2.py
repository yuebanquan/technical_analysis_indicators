import pandas as pd
import tradingStrategy as ts
import time
import Utils

# 开始运行时间
startTime = time.time()

stockDataFile = r"../StockData2.xlsx"
resultFile = r"./result/"
bestDfFile = resultFile + "2_1_最佳参数组合交易明细.csv"
backtestTradingDfFile = resultFile + "2_2_最佳参数组合交易明细.csv"
backtestYearTotalRateDfFile = resultFile + "2_3_每年收益明细"
FRDfFile = resultFile + "2_4_标的与净资产涨跌幅明细.csv"
frFile = resultFile + "2_5_标的与净资产涨跌幅对照图.png"
resultSrFile = resultFile + "2_6_策略结果.csv"
bestDfFile = resultFile + "2_1_最佳参数组合交易明细.csv"

backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'
initBalance = 1000000

shortEMARange = range(1, 16)
meduimEMARange = range(25, 100, 5)
DEA1Range = range(-100, 101)
DEA2Range = range(-100, 101)

sampleYear = 8

df = pd.read_excel(stockDataFile, sheet_name=1, index_col='Date', parse_dates=['Date'])

emaDf = ts.getEMADf(df, emaRange=range(1, 101))
macdDf = ts.getMACDDf(df)

print("样本内年份为：" + str(sampleYear))

# bestDf = ts.slidingWindowTrading(df, emaDf, macdDf,
#                                  backtestStartDate,
#                                  backtestEndDate,
#                                  sampleYear,
#                                  shortEMARange, meduimEMARange,
#                                  DEA1Range, DEA2Range,
#                                  initBalance)
#
# bestDf.to_csv(bestDfFile, encoding='utf-8-sig', index=False)

bestDf, backtestTradingDf, backtestYearTotalRateDf, resultSr = ts.slidingWindowTrading(df, emaDf, macdDf,
                                                                                       backtestStartDate,
                                                                                       backtestEndDate,
                                                                                       sampleYear,
                                                                                       shortEMARange, meduimEMARange,
                                                                                       DEA1Range, DEA2Range,
                                                                                       initBalance)

# 画出每日净资产涨跌幅与标的涨跌幅对照图
newTradingDf = ts.getNewTradingDf(df, backtestTradingDf, backtestStartDate, backtestEndDate)
preBacktestStartDate = Utils.getPreDate(df, backtestStartDate)
closeStd = df.loc[preBacktestStartDate, 'Close']
FRDf = ts.getFR(newTradingDf, frFile, closeStd, initBalance)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13] + 's'
resultSr['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
resultSr['程序运行时长'] = runTime

# 保存输出数据
bestDf.to_csv(bestDfFile, encoding='utf-8-sig', index=False)
backtestTradingDf.to_csv(backtestTradingDfFile, encoding='utf-8-sig')
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)
FRDf.to_csv(FRDfFile, encoding='utf-8-sig')
backtestYearTotalRateDf.to_csv(backtestYearTotalRateDfFile, encoding='utf-8-sig')
