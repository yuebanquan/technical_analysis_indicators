# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time


# 开始运行时间
startTime1 = time.time()

stockData = r"./StockData.xlsx"     # 股票数据路径
result3_1File = r'./result/step4_1.csv'    # 结果保存路径
result3_2File = r'./result/step4_2.csv'    # 结果保存路径
result3_3File = r'./result/step4_3.csv'    # 结果保存路径

backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'
initBalance = 1000000
lowShortMA = 1
highShortMA = 8
lowMediumMA = 5
highMediumMA = 21
lowLongMA = 120
highLongMA = 180
sampleYear=8

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

for sampleYear in range(8, 9):
    # 该样本内年份开始运行时间
    startTime = time.time()
    
    print("样本内年份为：" + str(sampleYear))
    bestMADf, backtestTradingDf, revenues = ts.slidingWindowTrading(df, backtestStartDate, backtestEndDate, sampleYear, lowShortMA, highShortMA, lowMediumMA, highMediumMA, lowLongMA, highLongMA, initBalance)
    
    saveFile = "./result/" + str(sampleYear) + "/"
    saveFile1= saveFile + "1.csv"
    saveFile2= saveFile + "2.csv"
    saveFile3= saveFile + "3.csv"
    
    # 结束运行时间
    endTime = time.time()
    # 计算程序运行时间
    runTime = str(endTime - startTime)[:-13]+'s'
    revenues['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
    revenues['程序运行时长'] = runTime
    
    bestMADf.to_csv(saveFile1, encoding='utf-8-sig', index=False)
    backtestTradingDf.to_csv(saveFile2,  encoding='utf-8-sig')
    revenues.to_csv(saveFile3, encoding='utf-8-sig', header= False)

# 结束运行时间
endTime1 = time.time()
# 计算程序运行时间
runTime1 = str(endTime1 - startTime1)[:-13]+'s'
print(runTime1)

