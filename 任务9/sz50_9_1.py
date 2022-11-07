import pandas as pd
import time
import datetime
import tradingStrategy as ts

# 开始运行时间
startTime = time.time()

# 数据集路径
stockDataFile = r"./StockData.xlsx"

# 结果路径
savePath = r'./result/sz50_9_1/'
bestDfPath = savePath + '1_bestDf.csv'
backtestTradingDfPath = savePath + "2_backtestTradingDf.csv"
resultSrPath = savePath + "3_resultSr.csv"

# 样本内区间
sampleStartDate = datetime.datetime.strptime('2005-1-4', '%Y-%m-%d')
sampleEndDate = datetime.datetime.strptime('2013-12-31', '%Y-%m-%d')
# 样本外区间
backtestStartDate = datetime.datetime.strptime('2014-01-02', '%Y-%m-%d')
backtestEndDate = datetime.datetime.strptime('2022-9-30', '%Y-%m-%d')

# 初试现金、参数范围、样本内数据量/年、滑动窗口步长/月
initBalance = 1000000  # 初试现金
shortMARange = range(1, 16)  # 短期均线范围
mediumMARange = range(20, 101)  # 中期均线范围
sampleDataSize = 9  # 样本内数据量/年
stepMonth = 1  # 滑动窗口步长/月

# 读取数据集
df = pd.read_excel(stockDataFile, sheet_name='sz50', index_col='Date', parse_dates=['Date'])

bestDf, backtestTradingDf, resultSr = ts.slidingWindowTrading(df,
                                                              backtestStartDate, stepMonth,
                                                              backtestEndDate, sampleDataSize,
                                                              shortMARange, mediumMARange,
                                                              initBalance
                                                              )

# 结束运行时间
endTime = time.time()
runTime = str(endTime - startTime)[:-13] + 's'
print(runTime)
resultSr['程序运行时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
resultSr['程序运行时长'] = runTime

# 保存输出数据
bestDf.to_csv(bestDfPath, encoding='utf-8-sig', index=False)
backtestTradingDf.to_csv(backtestTradingDfPath, encoding='utf-8-sig')
resultSr.to_csv(resultSrPath, encoding='utf-8-sig', header=False)
