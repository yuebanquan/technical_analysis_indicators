import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r"../StockData2.xlsx"
tradingDfFile = r"./result/tradingDf.csv"

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

df = pd.read_excel(stockDataFile, sheet_name=0, index_col='Date', parse_dates=['Date'])

strategyDf = ts.strategy1(df, startDate, endDate, MA=240)


tradingDf = ts.trading(strategyDf)

tradingDf.to_csv(tradingDfFile)
