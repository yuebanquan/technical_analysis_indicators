import pandas as pd
import tradingStrategy as ts
import Utils
import time

# 开始运行时间
startTime = time.time()

stockDataFile = r"../StockData2.xlsx"
tradingDfFile = r"./result/tradingDf.csv"
frFile = r"./result/fr.png"
1
startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000

df = pd.read_excel(stockDataFile, sheet_name=1, index_col='Date', parse_dates=['Date'])

emaDf = ts.getEMADf(df, emaRange=range(1, 101))
macdDf = ts.getMACDDf(df)

strategyDf = ts.strategy(df, emaDf, macdDf, startDate, endDate, shortEMA=10, mediumEMA=38, DEA1=10, DEA2=10)
tradingDf = ts.trading(strategyDf)

newTradingDf = ts.getNewTradingDf(df, tradingDf, startDate, endDate)
preStartDate = Utils.getPreDate(df, startDate)
closeStd = df.loc[preStartDate, 'Close']
FRDf = ts.getFR(newTradingDf, frFile, closeStd, initBalance)

# tradingDf.to_csv(tradingDfFile)

# 结束运行时间
endTime = time.time()
runTime = str(endTime - startTime)[:-13] + 's'
print(runTime)
