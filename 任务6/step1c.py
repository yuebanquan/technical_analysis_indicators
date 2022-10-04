import pandas as pd
import tradingStrategyC as ts
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r'./KDJ.csv'

step = '1c'
itAllStrategyDfFile = r'./result/' + step + '/' + step + '_itAllStrategyDf.csv'
bestTradingDfFile = r'./result/' + step + '/' + step + '_bestTradingDf.csv'
yearTotalRateDfFile = r'./result/' + step + '/' + step + '_yearTotalRateDf.csv'
resultSrFile = r'./result/' + step + '/' + step + '_resultSr.csv'
FRDfFile = r'./result/' + step + '/' + step + '_FRDf.csv'
frFile = r'./result/' + step + '/' + step + '_fr.png'

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

buyJRange = range(10, 91)
sellJRange = range(30, 111)

df = pd.read_csv(stockDataFile, index_col='Date', parse_dates=['Date'])

# 计算所有组合
itAllStrategyDf = ts.getAllStrategy(df, startDate, endDate, buyJRange, sellJRange)
# 计算最佳组合
bestBuyJ, bestSellJ, bestNetAsset = ts.getBestStrategy(itAllStrategyDf)
# 计算最佳组合明细
bestStrategyDf = ts.strategy(df, startDate, endDate, bestBuyJ, bestSellJ)
bestTradingDf = ts.trading(bestStrategyDf)
# 扩充最佳组合明细
newTradingDf = ts.getNewTradingDf(df, bestTradingDf, startDate, endDate)

# 计算总收益 & 年复利 & 最大回测率 & 年收益率表 & 夏普率
totalRate = ts.getTotalRate(initBalance, bestNetAsset)
compoundRate = ts.getCompoundRate(totalRate, startDate, endDate)
maxDrawDown = ts.getMaxDrawDown(newTradingDf)
yearTotalRateDf = ts.getYearTotalRateDf(newTradingDf, startDate, endDate)
sharpeRatio = ts.getSharpRatio(yearTotalRateDf)
resultSr = pd.Series([bestBuyJ, bestSellJ, bestNetAsset, totalRate, compoundRate, maxDrawDown, sharpeRatio],
                     index=['最佳J1', '最佳J2', '本期净资产', '本期总收益', '本期年复利', '最大回测率', '夏普率'])

# 画出每日净资产涨跌幅与标的涨跌幅对照图
FRDf = ts.getFR(newTradingDf, frFile)

# 结束运行时间
endTime = time.time()
resultSr['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
resultSr['程序运行时长'] = str(endTime - startTime)[:-13] + 's'

# 保存输出结果
itAllStrategyDf.to_csv(itAllStrategyDfFile, encoding='utf-8-sig', index=False)
bestTradingDf.to_csv(bestTradingDfFile, encoding='utf-8-sig')
yearTotalRateDf.to_csv(yearTotalRateDfFile, encoding='utf-8-sig')
resultSr.to_csv(resultSrFile, encoding='utf-8-sig', header=False)
FRDf.to_csv(FRDfFile, encoding='utf-8-sig')
