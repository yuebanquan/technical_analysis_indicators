import pandas as pd
import tradingStrategy as ts

stockDataFile = r'./StockData.xlsx'

startDate = '2006-01-04'
endDate = '2021-12-31'
initBalance = 1000000
hold = 0
longEMA = 120
df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

strategyDf = ts.shortEMAAndMediumEMAStrategy(df, startDate, endDate, shortEMA=15, mediumEMA=100)
tradingDf = ts.trading(strategyDf, startDate, endDate)

tradingDf.to_csv(r"./result/test.csv")
