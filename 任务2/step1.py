# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()


stockDataFile = r'./StockData.xlsx'
tradingDfFile = r'./result/step1_1.csv'
result1_2File = r'./result/step1_2.csv'
startDate = '2006-01-04'
endDate = '2021-12-31'
shortMA = 5
mediumMA = 20
initBalance = 1000000

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

strategyDf = ts.DoubleMAStrategy(df, startDate, endDate, shortMA, mediumMA)

tradingDf = ts.trading(strategyDf, startDate, endDate)

# 将结果保存为csv
tradingDf.to_csv(tradingDfFile, encoding='utf-8-sig')


# 计算本期净资产、总收益率、年均收益率复利
netAsset = tradingDf.iloc[-1]['netAsset']
totalRate = ts.getTotalRate(initBalance, netAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

# 使用Series保存：本期净资产, 总收益率, 年均收益率复利, 程序运行时间, 程序运行时长
result1_2 = pd.Series([netAsset, totalRate, compoundRate, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime)), runTime], index=['本期净资产', '总收益率', '年均收益率复利', '程序运行时间', '程序运行时长'])

# 将结果保存为csv
result1_2.to_csv(result1_2File, encoding='utf-8-sig')






