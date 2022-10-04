# -*- coding: utf-8 -*-
import pandas as pd
import tradingStrategy as ts
import time


# 开始运行时间
startTime = time.time()

initMoney = 1000000
lowMA = 120
highMA = 240
sampleStartDate = '2006-01-04'
sampleEndDate = '2013-12-31'
backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'
stockData = r"./StockData.xlsx"     # 股票数据路径
result3_1File = r'./result/step3_1.csv'    # 结果保存路径
result3_2File = r'./result/step3_2.csv'    # 结果保存路径
result3_3File = r'./result/step3_3.csv'    # 结果保存路径
result3_4File = r'./result/step3_4.csv'    # 结果保存路径

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

# 寻找最佳MA
result3_1 = ts.getMAAndNetAsset(df, sampleStartDate, sampleEndDate)
bestMA = result3_1.astype('int64').idxmax()[0]
sampleNetAsset = result3_1.loc[bestMA, 'netAsset']
sampleTotalRate = ts.getTotalRate(initMoney, sampleNetAsset)
sampleCompoundRate = ts.getCompoundRate(sampleTotalRate, sampleStartDate, sampleEndDate)

# 保存为csv
result3_1.to_csv(result3_1File, encoding='utf-8-sig')
result3_2 = pd.Series([bestMA, sampleNetAsset, sampleTotalRate, sampleCompoundRate], index=['最佳长期均线', '样本净资产', '样本总收益率', '样本年均收益率复利'])
result3_2.to_csv(result3_2File, encoding='utf-8-sig', header= False)


# 回测
result3_3 = ts.strategy(df, backtestStartDate, backtestEndDate, bestMA)
backtestNetAsset = result3_3.iloc[-1]['netAsset']
backtestTotalRate = ts.getTotalRate(initMoney, backtestNetAsset)
backtestCompoundRate = ts.getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'


# 保存为csv
result3_3.to_csv(result3_3File, encoding='utf-8-sig')
result3_4 = pd.Series([backtestNetAsset, backtestTotalRate, backtestCompoundRate, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime)), runTime], index=['回测净资产', '回测总收益率', '回测年均收益率复利', '程序运行时间', '程序运行时长'])
result3_4.to_csv(result3_4File, encoding='utf-8-sig', header= False)



print("最佳长期均线为MA" + str(bestMA))
print("该策略回测净资产为" + str(backtestNetAsset) + "元。")


