# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r'./StockData.xlsx'
startDate = '2006-01-04'
endDate = '2021-12-31'

initBalance = 1000000
lowShortMA = 1
highShortMA = 8
lowMediumMA = 5
highMediumMA = 21
lowLongMA = 120
highLongMA = 180

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

MAAndNetAssetDf = ts.getMAAndNetAsset(df, startDate, endDate, lowShortMA, highShortMA, lowMediumMA, highMediumMA, lowLongMA, highLongMA)
bestStrategy = ts.getBestStrategy(MAAndNetAssetDf)
totalRate = ts.getTotalRate(initBalance, bestStrategy['本期净资产'])
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)
bestStrategy['总收益率'] = totalRate
bestStrategy['年均收益率复利'] = compoundRate

MAAndNetAssetDf.to_csv(r"./result/step1_1.csv", encoding='utf-8-sig', index=False)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'
bestStrategy['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime))
bestStrategy['程序运行时长'] = runTime

bestStrategy.to_csv(r"./result/step1_2.csv", encoding='utf-8-sig', header= False)
