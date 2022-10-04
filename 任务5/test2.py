import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r"./MACD.csv"


startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date']).loc['2005-12-30':endDate]

preDEA = df['DEA'].shift(1)
preDEA = preDEA<-100
print(preDEA)
