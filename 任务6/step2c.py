import pandas as pd
import tradingStrategyC as ts
import time
import Utils

# 开始运行时间
startTime = time.time()

stockDataFile = r'./KDJ.csv'

step = '2c'
saveFile = "./result/" + step + "/"
bestDDfFile = saveFile + "1_bestDDf.csv"
backtestTradingDfFile = saveFile + "2_backtestTradingDf.csv"
resultSrFile = saveFile + "3_resultSr.csv"
frFile = saveFile + "4_fr.png"
FRDfFile = saveFile + "5_frDf.csv"

backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'
initBalance = 1000000
sampleYear = 8

buyJRange = range(10, 91)
sellJRange = range(30, 111)

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

# 该样本内年份开始运行时间
startTime = time.time()

# 滑动窗口运算
print("样本内年份为：" + str(sampleYear))
bestDDf, backtestTradingDf, resultSr = ts.slidingWindowTrading(df, backtestStartDate, backtestEndDate, sampleYear,
                                                               buyJRange, sellJRange, initBalance)

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
bestDDf.to_csv(bestDDfFile, encoding='utf-8-sig', index=False)
backtestTradingDf.to_csv(backtestTradingDfFile, encoding='utf-8-sig')
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)
FRDf.to_csv(FRDfFile, encoding='utf-8-sig')

# 打印运行时长
print(runTime)
