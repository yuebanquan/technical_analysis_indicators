# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

EMAAndNetAssetDfFile = r"./result/step1_1.csv"
bestStrategyFile = r"./result/step1_2.csv"
stockDataFile = r'./StockData.xlsx'

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000
lowLongEMA = 120
highLongEMA = 240

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

EMAAndNetAssetDf = ts.getEMAAndNetAsset1(df, startDate, endDate, lowLongEMA, highLongEMA, initBalance)
bestLongEMA, bestNetAsset = ts.getBestStrategy1(EMAAndNetAssetDf)
totalRate = ts.getTotalRate(initBalance, bestNetAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)
bestStrategy = pd.Series([bestLongEMA, bestNetAsset, totalRate, compoundRate],
                         index=['最佳长期EMA', '最佳净资产', '总收益率', '年均收益率复利'])
# 结束运行时间
endTime = time.time()
# 计算程序运行时间和开始运行时间
bestStrategy['程序运行时长'] = str(endTime - startTime)[:-13] + 's'
bestStrategy['程序开始运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))


EMAAndNetAssetDf.to_csv(EMAAndNetAssetDfFile, encoding='utf-8-sig', index=False)
bestStrategy.to_csv(bestStrategyFile, encoding='utf-8-sig', header=False)
