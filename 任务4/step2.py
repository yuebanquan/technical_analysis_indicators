import pandas as pd
import time
import tradingStrategy as ts

# 开始运行时间
startTime = time.time()

stockData = r"./StockData.xlsx"                    # 股票数据路径
EMAAndNetAssetDfFile = r'./result/step2_1.csv'      # 结果保存路径
sampleDfFile = r'./result/step2_2.csv'             # 结果保存路径
backtestTradingDfFile = r'./result/step2_3.csv'    # 结果保存路径
backtestDfFile = r'./result/step2_4.csv'           # 结果保存路径

sampleStartDate = '2006-01-04'
sampleEndDate = '2013-12-31'
backtestStartDate = '2014-01-02'
backtestEndDate = '2021-12-31'
initBalance = 1000000
lowShortEMA = 1
highShortEMA = 15
lowMediumEMA = 20
highMediumEMA = 100

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_excel(stockData, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

# 寻找最佳短期和中期EMA
EMAAndNetAssetDf = ts.getEMAAndNetAsset2(df, sampleStartDate, sampleEndDate, lowShortEMA, highShortEMA, lowMediumEMA, highMediumEMA)
bestShortEMA, bestMediumEMA, sampleNetAsset = ts.getBestStrategy2(EMAAndNetAssetDf)

# 计算样本内区间收益率和复利
sampleTotalRate = ts.getTotalRate(initBalance, sampleNetAsset)
sampleCompoundRate = ts.getCompoundRate(sampleTotalRate, sampleStartDate, sampleEndDate)
sampleDf = pd.Series([bestShortEMA, bestMediumEMA, sampleNetAsset, sampleTotalRate, sampleCompoundRate], index=['最佳短期EMA', '最佳中期EMA', '样本净资产', '样本总收益率', '样本年均收益率复利'])

# 回测
backtestStrategyDf = ts.shortEMAAndMediumEMAStrategy(df, backtestStartDate, backtestEndDate, bestShortEMA, bestMediumEMA)
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
EMAAndNetAssetDf.to_csv(EMAAndNetAssetDfFile, encoding='utf-8-sig', index=False)
sampleDf.to_csv(sampleDfFile, encoding='utf-8-sig', header= False)
backtestTradingDf.to_csv(backtestTradingDfFile, encoding='utf-8-sig')
backtestDf.to_csv(backtestDfFile, encoding='utf-8-sig', header= False)

