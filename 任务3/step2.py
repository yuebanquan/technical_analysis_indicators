# -*- coding: utf-8 -*-
import pandas as pd
import time
import tradingStrategy as ts


# 开始运行时间
startTime = time.time()

stockData = r"./StockData.xlsx"                    # 股票数据路径
MAAndNetAssetDfFile = r'./result/step2_1.csv'      # 结果保存路径
sampleDfFile = r'./result/step2_2.csv'             # 结果保存路径
backtestTradingDfFile = r'./result/step2_3.csv'    # 结果保存路径
backtestDfFile = r'./result/step2_4.csv'           # 结果保存路径

sampleStartDate = '2006-01-04'
sampleEndDate = '2013-12-31'
backtestStartDate = '2014-01-02'
backtestEndDate = '2021-12-31'
initBalance = 1000000
lowShortMA = 1
highShortMA = 8
lowMediumMA = 5
highMediumMA = 21
lowLongMA = 120
highLongMA = 180

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

# 寻找最佳短期、中期、长期均线
MAAndNetAssetDf = ts.getMAAndNetAsset(df, sampleStartDate, sampleEndDate, lowShortMA, highShortMA, lowMediumMA, highMediumMA, lowLongMA, highLongMA)
bestStrategy = ts.getBestStrategy(MAAndNetAssetDf)
bestShortMA = int(bestStrategy['最佳短期均线'])
bestMediumMA = int(bestStrategy['最佳中期均线'])
bestLongMA = int(bestStrategy['最佳长期均线'])
sampleNetAsset = bestStrategy['本期净资产']

# 计算样本内区间收益率和复利
sampleTotalRate = ts.getTotalRate(initBalance, sampleNetAsset)
sampleCompoundRate = ts.getCompoundRate(sampleTotalRate, sampleStartDate, sampleEndDate)
sampleDf = pd.Series([bestShortMA, bestMediumMA, bestLongMA, sampleNetAsset, sampleTotalRate, sampleCompoundRate], index=['最佳短期均线', '最佳中期均线', '最佳长期均线', '样本净资产', '样本总收益率', '样本年均收益率复利'])

# 回测
backtestStrategyDf = ts.longMAAndDoubleMAStrategy(df, backtestStartDate, backtestEndDate, bestShortMA, bestMediumMA, bestLongMA)
backtestTradingDf = ts.trading(backtestStrategyDf, backtestStartDate, backtestEndDate)

backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
backtestTotalRate = ts.getTotalRate(initBalance, backtestNetAsset)
backtestCompoundRate = ts.getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)

# 结束运行时间
endTime = time.time()
# 计算程序运行时间
runTime = str(endTime - startTime)[:-13]+'s'

backtestDf = pd.Series([backtestNetAsset, backtestTotalRate, backtestCompoundRate, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(startTime)), runTime], index=['回测净资产', '回测总收益率', '回测年均收益率复利', '程序运行时间', '程序运行时长'])

# 保存结果至csv
MAAndNetAssetDf.to_csv(MAAndNetAssetDfFile, encoding='utf-8-sig', index=False)
sampleDf.to_csv(sampleDfFile, encoding='utf-8-sig', header= False)
backtestTradingDf.to_csv(backtestTradingDfFile, encoding='utf-8-sig')
backtestDf.to_csv(backtestDfFile, encoding='utf-8-sig', header= False)
