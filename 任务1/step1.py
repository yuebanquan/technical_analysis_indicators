# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time


# 开始运行时间
startTime = time.time()

startDate = '2006-01-04'
endDate = '2021-12-31'
testMA = 240
initMoney = 1000000
stockData = r"./StockData.xlsx"     # 股票数据路径
result1_1File = r'./result/step1_1.csv' # 结果保存路径
result1_2File = r'./result/step1_2.csv' # 结果保存路径
netAsset =0         # 本期净资产
totalRate = 0       # 总收益率
compoundRate = 0    # 复利


# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

# 交易
result1_1 = ts.strategy(df, startDate, endDate, testMA, initMoney)
result1_1 = ts.trading(result1_1, startDate, endDate)
netAsset = result1_1.iloc[-1]['netAsset']  # 获取本期净资产
totalRate = ts.getTotalRate(initMoney, netAsset)    # 计算总收益率
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)  # 计算年均收益率复利

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

# 使用Series保存：本期净资产, 总收益率, 年均收益率复利, 程序运行时间, 程序运行时长
result1_2 = pd.Series([netAsset, totalRate, compoundRate, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime)), runTime], index=['本期净资产', '总收益率', '年均收益率复利', '程序运行时间', '程序运行时长'])

# 输出结果
print("交易区间：" + startDate + " to " + endDate)
print("本金：1000000元")
print('本期净资产：{:.2f}元\n总收益率：{}\n年均收益率复利：{}'.format(netAsset, totalRate, compoundRate))
print('程序运行时间：' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime)))
print('程序运行时长：' + runTime)

# 保存为csv
result1_1.to_csv(result1_1File, encoding='utf-8-sig')
result1_2.to_csv(result1_2File, encoding='utf-8-sig', header= False)





