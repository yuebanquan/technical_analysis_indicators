import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r"./MACD.csv"
itAllStrategyDfFile = r"./result/2_1.csv"
resultSrFile = r"./result/2_2.csv"

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

strategyDf = ts.strategy2(df,startDate,endDate,-100, -100, showPreIndicator=True)
tradingDf = ts.trading(strategyDf)

tradingDf.to_csv(r"./result/test.csv")
# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13] + 's'
print(runTime)
