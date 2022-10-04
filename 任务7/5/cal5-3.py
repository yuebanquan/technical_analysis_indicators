import pandas as pd
import tradingStrategy as ts
import time
import Utils

# 开始运行时间
startTime = time.time()

stockDataFile = r"./MACD.csv"
backtestTradingDfFile = r'./result/2_backtestTradingDf.csv'
resultSrFile = r'./result/3_resultSr.csv'
frFile = r'./result/4_fr.png'
FRDfFile = r'./result/5_frDf.csv'


backtestStartDate = '2014-1-2'
backtestEndDate = '2021-12-31'

initBalance = 1000000
sampleYear = 8

# 读取沪深300指数的开盘价、收盘价，并将日期作为索引
df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

# 读取最佳回测交易记录
backtestTradingDf = pd.read_csv(backtestTradingDfFile, index_col='Date', parse_dates=['Date'])

# 扩充最佳回测交易记录
newTradingDf = ts.getNewTradingDf(df, backtestTradingDf, backtestStartDate, backtestEndDate)

# 画出每日净资产涨跌幅与标的涨跌幅对照图
preBacktestStartDate = Utils.getPreDate(df, backtestStartDate)
closeStd = df.loc[preBacktestStartDate, 'Close']
FRDf = ts.getFR(newTradingDf, frFile, closeStd, initBalance)

# 计算净资产 & 总收益率 & 年复利 & 最大回撤率
backtestNetAsset = backtestTradingDf.iloc[-1]['netAsset']
backtestTotalRate = ts.getTotalRate(initBalance, backtestNetAsset)
backtestCompoundRate = ts.getCompoundRate(backtestTotalRate, backtestStartDate, backtestEndDate)
backtestMaxDrawDown = ts.getMaxDrawDown(newTradingDf)
backtestYearTotalRateDf = ts.getYearTotalRateDf(newTradingDf, backtestStartDate, backtestEndDate)
backtestSharpeRatio = ts.getSharpRatio(backtestYearTotalRateDf)
resultSr = pd.Series([sampleYear, backtestNetAsset, backtestTotalRate, backtestCompoundRate, backtestMaxDrawDown,
                      backtestSharpeRatio],
                     index=['样本内数据年份数', '样本外净资产', '总收益率', '年复利', '最大回撤率', '夏普率'])


# 保存输出数据
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)
FRDf.to_csv(FRDfFile, encoding='utf-8-sig')