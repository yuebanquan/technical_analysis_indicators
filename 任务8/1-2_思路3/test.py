import pandas as pd
import tradingStrategy as ts
import time
import Utils

# 开始运行时间
startTime = time.time()

stockDataFile = r"../StockData2.xlsx"
resultFile = r"./result/"
itAllStrategyDfFile = resultFile + "1_1_所有参数组合.csv"
bestTradingDfFile = resultFile + "1_2_最佳参数组合交易明细.csv"
yearTotalRateDfFile = resultFile + "1_3_每年收益明细.csv"
FRDfFile = resultFile + "1_4_标的与净资产涨跌幅明细.csv"
frFile = resultFile + "1_5_标的与净资产涨跌幅对照图.png"
resultSrFile = resultFile + "1_6_策略结果.csv"

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

MA = 141
DEA1 = 27
DEA2 = -5

df = pd.read_excel(stockDataFile, sheet_name=0, index_col='Date', parse_dates=['Date'])

# 计算最佳组合明细
strategyDf = ts.strategy(df, startDate, endDate, MA, DEA1, DEA2)
tradingDf = ts.trading(strategyDf)
netAsset = tradingDf.iloc[-1]['netAsset']

# 扩充最佳组合明细
newTradingDf = ts.getNewTradingDf(df, tradingDf, startDate, endDate)

# 计算总收益 & 年复利 & 最大回测率 & 年收益率表 & 夏普率
totalRate = ts.getTotalRate(initBalance, tradingDf)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)
maxDrawDown = ts.getMaxDrawDown(newTradingDf)
yearTotalRateDf = ts.getYearTotalRateDf(newTradingDf, startDate, endDate)
sharpeRatio = ts.getSharpRatio(yearTotalRateDf)
resultSr = pd.Series([MA, DEA1, DEA2, netAsset, totalRate, compoundRate, maxDrawDown, sharpeRatio],
                     index=['最佳MA', '最佳DEA1','最佳DEA2', '本期净资产', '本期总收益', '本期年复利', '最大回测率', '夏普率'])

# 画出每日净资产涨跌幅与标的涨跌幅对照图
preStartDate = Utils.getPreDate(df, startDate)
closeStd = df.loc[preStartDate, 'Close']
FRDf = ts.getFR(newTradingDf, frFile, closeStd=closeStd, netAssetStd=initBalance)

# 结束运行时间
endTime = time.time()
resultSr['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
resultSr['程序运行时长'] = str(endTime - startTime)[:-13] + 's'


tradingDf.to_csv(bestTradingDfFile, encoding='utf-8-sig')
yearTotalRateDf.to_csv(yearTotalRateDfFile, encoding='utf-8-sig')
FRDf.to_csv(FRDfFile, encoding='utf-8-sig')
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)