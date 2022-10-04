# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import Utils
import time


# 开始运行时间
startTime = time.time()

stockData = r"./StockData.xlsx"     # 股票数据路径
result3_1File = r'./result/step3_1.csv'    # 结果保存路径
result3_2File = r'./result/step3_2.csv'    # 结果保存路径
result3_3File = r'./result/step3_3.csv'    # 结果保存路径

initBalance = 1000000
lowShortMA = 1
highShortMA = 8
lowMediumMA = 5
highMediumMA = 21
lowLongMA = 120
highLongMA = 180

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

balance = initBalance
netAsset = initBalance
hold = 0
sampleYear = 8
backtestYear = 8
sampleStartYear = 2006
sampleEndYear = sampleStartYear + sampleYear
backtestStartYear = 2014
backtestEndYear = backtestStartYear + backtestYear
backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'

backtestTradingDf = pd.DataFrame(columns=['Open', 'Close', 'sign', 'hold', 'balance', 'netAsset', 'profit'])

yearDf =  pd.DataFrame(columns=['startDate','endDate'])
for year in range(2006, 2022):
    yearDf.loc[year] = [Utils.getFirstDate(df, year), Utils.getLastDate(df, year)]
# print(yearDf)

result3_1 = pd.DataFrame(columns=['样本内数据年份数', '第iyear窗口', '最佳短期均线','最佳中期均线','最佳长期均线', '样本内净资产'])


for iyear in range(0, sampleYear):
    # print(i+sampleStartYear)
    # 计算
    year = sampleStartYear + iyear
    sampleStartDate = yearDf.loc[year, 'startDate']    # 样本开始日期
    sampleEndDate = yearDf.loc[year+sampleYear-1, 'endDate']      # 样本结束日期
    
    backtestStartDate = yearDf.loc[backtestStartYear+iyear, 'startDate'] # 回测开始日期
    backtestEndDate = yearDf.loc[backtestStartYear+iyear, 'endDate']     # 回测结束日期
    print(backtestStartDate + " to " + backtestEndDate)
    
    sampleMAAndNetAssetDf = ts.getMAAndNetAsset(df, sampleStartDate, sampleEndDate, lowShortMA, highShortMA, lowMediumMA, highMediumMA, lowLongMA, highLongMA)
    bestID = sampleMAAndNetAssetDf['netAsset'].idxmax()
    bestShortMA = sampleMAAndNetAssetDf.loc[bestID, 'shortMA']
    bestMediumMA = sampleMAAndNetAssetDf.loc[bestID, 'mediumMA']
    bestLongMA = sampleMAAndNetAssetDf.loc[bestID, 'longMA']
    sampleMostNetAsset = sampleMAAndNetAssetDf.loc[bestID, 'netAsset']
    print("最佳短期均线 = "+str(bestShortMA))
    print("最佳中期均线 = "+str(bestMediumMA))
    print("最佳长期均线 = "+str(bestLongMA))
    
    result3_1.loc[iyear] = [sampleYear, iyear, bestShortMA, bestMediumMA, bestLongMA, sampleMostNetAsset]
    backtestStrategyDf = ts.longMAAndDoubleMAStrategy(df, backtestStartDate, backtestEndDate, bestShortMA, bestMediumMA, bestLongMA)
    backtestTradingDf = backtestTradingDf.append(ts.trading(backtestStrategyDf, backtestStartDate, backtestEndDate, balance, hold))
    
    balance = backtestTradingDf.iloc[-1]['balance']
    hold = backtestTradingDf.iloc[-1]['hold']
    netAsset = backtestTradingDf.iloc[-1]['netAsset']
    print("本年交易结束后净资产 = " + str(netAsset))
    print("=============================================")

backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
backtestTotalRate = ts.getTotalRate(initBalance, backtestNetAsset)
backtestCompoundRate = ts.getCompoundRate(backtestTotalRate, '2014-1-2', '2021-12-31')

print(backtestNetAsset)
print(backtestTotalRate)
print(backtestCompoundRate)
# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

result3_3 = pd.Series([sampleYear, backtestNetAsset, backtestCompoundRate, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime)), runTime], index=['样本内数据年份数', '样本外净资产', '年均收益率复利', '程序运行时间', '程序运行时长'])


result3_1.to_csv(result3_1File, encoding='utf-8-sig', index=False)
backtestTradingDf.to_csv(result3_2File, encoding='utf-8-sig')
result3_3.to_csv(result3_3File, encoding='utf-8-sig', header= False)

