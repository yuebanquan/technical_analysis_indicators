# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import Utils
import time


# 开始运行时间
startTime = time.time()

initMoney = 1000000
lowMA = 120
highMA = 240
stockData = r"./StockData.xlsx"     # 股票数据路径
result4_1File = r'./result/step4_1.csv'    # 结果保存路径
result4_2File = r'./result/step4_2.csv'    # 结果保存路径
result4_3File = r'./result/step4_3.csv'    # 结果保存路径


# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

balance = initMoney
netAsset = initMoney
hold = 0
sampleYear = 8
backtestYear = 8
sampleStartYear = 2006
sampleEndYear = sampleStartYear + sampleYear
backtestStartYear = 2014
backtestEndYear = backtestStartYear + backtestYear
backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'


backtestDf = pd.DataFrame(columns=['Open', 'Close', 'MA', 'sign', 'hold', 'balance', 'netAsset', 'profit'])

yearDf =  pd.DataFrame(columns=['startDate','endDate'])
for year in range(2006, 2022):
    yearDf.loc[year] = [Utils.getFirstDate(df, year), Utils.getLastDate(df, year)]
# print(yearDf)

result4_1 = pd.DataFrame(columns=['样本内数据年份数', '第iyear窗口', '最佳均线', '样本内净资产'])

for iyear in range(0, sampleYear):
    # print(i+sampleStartYear)
    # 计算
    year = sampleStartYear + iyear
    sampleStartDate = yearDf.loc[year, 'startDate']    # 样本开始日期
    sampleEndDate = yearDf.loc[year+sampleYear-1, 'endDate']      # 样本结束日期
    
    backtestStartDate = yearDf.loc[backtestStartYear+iyear, 'startDate'] # 回测开始日期
    backtestEndDate = yearDf.loc[backtestStartYear+iyear, 'endDate']     # 回测结束日期
    print(backtestStartDate + " to " + backtestEndDate)
    
    sampleMAAndNetAssetDf = ts.getMAAndNetAsset(df, sampleStartDate, sampleEndDate, lowMA, highMA)
    bestMA = sampleMAAndNetAssetDf.astype('int64').idxmax()[0]
    sampleMostNetAsset = sampleMAAndNetAssetDf.loc[bestMA, 'netAsset']
    print("最佳MA = "+str(bestMA))
    
    result4_1.loc[iyear] = [sampleYear, iyear, bestMA, sampleMostNetAsset]
    
    backtestDf = backtestDf.append(ts.strategy(df, backtestStartDate, backtestEndDate, bestMA, initMoney=balance, hold=hold))
    
    balance = backtestDf.iloc[-1]['balance']
    hold = backtestDf.iloc[-1]['hold']
    netAsset = backtestDf.iloc[-1]['netAsset']
    print("本年交易结束后净资产 = " + str(netAsset))
    print("=============================================")

backtestNetAsset = backtestDf.iloc[-1]['balance']
backtestTotalRate = ts.getTotalRate(initMoney, backtestNetAsset)
backtestCompoundRate = ts.getCompoundRate(backtestTotalRate, '2014-1-2', '2021-12-31')

print(backtestNetAsset)
print(backtestTotalRate)
print(backtestCompoundRate)
# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

result4_3 = pd.Series([sampleYear, backtestNetAsset, backtestCompoundRate, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime)), runTime], index=['样本内数据年份数', '样本外净资产', '年均收益率复利', '程序运行时间', '程序运行时长'])


result4_1.to_csv(result4_1File, encoding='utf-8-sig', index=False)
backtestDf.to_csv(result4_2File, encoding='utf-8-sig')
result4_3.to_csv(result4_3File, encoding='utf-8-sig', header= False)




    


