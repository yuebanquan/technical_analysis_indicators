import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r"./MACD.csv"
backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'
initBalance = 1000000
lowDEA1 = -100
highDEA1 = 100
lowDEA2 = -100
highDEA2 = 100

sampleYear = 8

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])


# 该样本内年份开始运行时间
startTime = time.time()

print("样本内年份为：" + str(sampleYear))
bestMACDDf, backtestTradingDf, revenues = ts.slidingWindowTrading(df, backtestStartDate, backtestEndDate,
                                                                  sampleYear, lowDEA1, highDEA1, lowDEA2, highDEA2,
                                                                  initBalance, debug=True)

saveFile = "./result/" + str(sampleYear) + "/"
saveFile1 = saveFile + "1.csv"
saveFile2 = saveFile + "2.csv"
saveFile3 = saveFile + "3.csv"

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13] + 's'
revenues['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
revenues['程序运行时长'] = runTime

bestMACDDf.to_csv(saveFile1, encoding='utf-8-sig', index=False)
backtestTradingDf.to_csv(saveFile2, encoding='utf-8-sig')
revenues.to_csv(saveFile3, encoding='utf-8-sig', header=False)

# 结束运行时间
endTime1 = time.time()
# 计算程序运行时间
runTime1 = str(endTime1 - startTime)[:-13] + 's'
print(runTime1)
