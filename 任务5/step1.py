import pandas as pd
import tradingStrategy as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r"./MACD.csv"
tradingDfFile = r"./result/1_1.csv"
resultSrFile = r'./result/1_2.csv'

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

strategyDf = ts.strategy1(df, startDate, endDate)
tradingDf = ts.trading(strategyDf, initBalance=initBalance)

netAsset = tradingDf.iloc[-1]['netAsset']
totalRate = ts.getTotalRate(initBalance, netAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)
resultSr = pd.Series([netAsset, totalRate, compoundRate], index=['本期净资产', '总收益率', '年均收益率复利'])

# 结束运行时间
endTime = time.time()
resultSr['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime))
resultSr['程序运行时长'] = str(endTime - startTime)[:-13]+'s'

tradingDf.to_csv(tradingDfFile, encoding='utf-8-sig')
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)