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

lowDEA1 = -100
highDEA1 = 100
lowDEA2 = -100
highDEA2 = 100

df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

itAllStrategyDf = ts.getAllStrategy(df, startDate, endDate, lowDEA1, highDEA1, lowDEA2, highDEA2)
bestDEA1, bestDEA2, bestNetAsset = ts.getBestStrategy(itAllStrategyDf)
totalRate = ts.getTotalRate(initBalance, bestNetAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)
resultSr = pd.Series([bestDEA1, bestDEA2, bestNetAsset, totalRate, compoundRate],
                     index=['最佳DEA1', '最佳DEA2', '本期净资产', '本期总收益', '本期年复利'])

# 结束运行时间
endTime = time.time()
resultSr['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
resultSr['程序运行时长'] = str(endTime - startTime)[:-13] + 's'

itAllStrategyDf.to_csv(itAllStrategyDfFile, encoding='utf-8-sig', index=False)
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)
