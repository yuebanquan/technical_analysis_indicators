# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000
stockDataFile = r'./StockData.xlsx'
MAAndNetAssetDfFile = r'./result/step2_1.csv'
result2_2File = r'./result/step2_2.csv'

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

MAAndNetAssetDf = ts.getMAAndNetAsset(df, startDate, endDate)

MAAndNetAssetDf.to_csv(MAAndNetAssetDfFile, encoding='utf-8-sig', index=False)

bestID = MAAndNetAssetDf['netAsset'].idxmax()
bestShortMA = MAAndNetAssetDf.loc[bestID, 'shortMA']
bestmediumMA = MAAndNetAssetDf.loc[bestID, 'mediumMA']
bestNetAsset = MAAndNetAssetDf.loc[bestID, 'netAsset']

totalRate = ts.getTotalRate(initBalance, bestNetAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

result2_2 = pd.Series([bestShortMA, bestmediumMA, bestNetAsset, totalRate, compoundRate, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime)), runTime], index=['最佳短期均线', '最佳中期均线', '本期净资产', '总收益率', '年均收益率复利', '程序运行时间', '程序运行时长'])

result2_2.to_csv(result2_2File, encoding='utf-8-sig')


