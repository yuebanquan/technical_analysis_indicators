# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time


# 开始运行时间
startTime = time.time()

startDate = '2006-01-04'
endDate = '2021-12-31'
initMoney = 1000000
stockData = r"./StockData.xlsx"     # 股票数据路径
result2_1File = r'./result/step2_1.csv'    # 结果保存路径
result2_2File = r'./result/step2_2.csv'    # 结果保存路径

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]
result2_1 = ts.getMAAndNetAsset(df, startDate, endDate)
bestMA = result2_1.astype('int64').idxmax()[0]
netAsset = result2_1.loc[bestMA, 'netAsset']
totalRate = ts.getTotalRate(initMoney, netAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

result2_2 = pd.Series([bestMA, netAsset, totalRate, compoundRate, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime)), runTime], index=['最佳长期均线', '本期净资产', '总收益率', '年均收益率复利', '程序运行时间', '程序运行时长'])

# 输出结果
print(result2_2)

# 将结果保存至csv
result2_1.to_csv(result2_1File, encoding='utf-8-sig')
result2_2.to_csv(result2_2File, encoding='utf-8-sig', header= False)


