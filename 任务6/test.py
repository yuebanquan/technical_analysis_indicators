import pandas as pd
import tradingStrategyB as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r'./KDJ.csv'

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000


df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])
strategyDf = ts.strategy(df, startDate, endDate, buyJ=43, sellJ=110)

tradingDf = ts.trading(strategyDf)