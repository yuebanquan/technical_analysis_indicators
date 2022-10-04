import pandas as pd
import tradingStrategy as ts
import time
import Utils

# 开始运行时间
startTime = time.time()

stockDataFile = r"../StockData2.xlsx"

bestDfFile = r"./result/1_bestDf.csv"
backtestTradingDfFile = r"./result/2_backtestTradingDf.csv"
resultSrFile = r"./result/3_resultSr.csv"
frFile = r"./result/4_fr.png"
FRDfFile = r"./result/5_FRDf.csv"
backtestYearTotalRateDfFile = r"./result/6_backtestYearTotalRateDf"

backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'
initBalance = 1000000

sampleYear = 8

df = pd.read_excel(stockDataFile, sheet_name=0, index_col='Date', parse_dates=['Date'])

print("样本内年份为：" + str(sampleYear))
bestDf, backtestTradingDf, resultSr, backtestYearTotalRateDf = ts.slidingWindowTrading(df, backtestStartDate,
                                                                                       backtestEndDate, sampleYear,
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
