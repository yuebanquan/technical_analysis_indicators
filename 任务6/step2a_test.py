import pandas as pd
import tradingStrategyA as ts
import time
import Utils

# 开始运行时间
startTime = time.time()

stockDataFile = r'./KDJ.csv'

step = '2a'
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

buyDRange = range(10, 91)
sellDRange = range(20, 101)

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

# 该样本内年份开始运行时间
startTime = time.time()

preBacktestStartDate = Utils.getPreDate(df, backtestStartDate)

