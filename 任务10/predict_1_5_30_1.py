import pandas as pd
import numpy as np
import datetime
import lRPredict

# 数据集路径
stockDataFile = r"./StockData.xlsx"
resultDfFile = r'./result/resultDf_1_5_30_1.csv'

# 样本内区间
sampleStartDate = datetime.datetime.strptime('2005-1-4', '%Y-%m-%d')
sampleEndDate = datetime.datetime.strptime('2013-12-31', '%Y-%m-%d')
# 样本外区间
backtestStartDate = datetime.datetime.strptime('2014-01-02', '%Y-%m-%d')
backtestEndDate = datetime.datetime.strptime('2022-9-30', '%Y-%m-%d')

# 参数
forecastDays = 1  # 预测未来第几天的股价
pastDays = 5  # 过去n日作为一组
maValue = 30  # MA取值
stepMonth = 1  # 滑动窗口步长,月
sampleDataSize = 9  # 样本内数据量: 9年

df = pd.read_excel(stockDataFile, sheet_name='sz50', index_col='Date', parse_dates=['Date'])  # 读取数据集

realPreDf, ratio = lRPredict.lRPredict(df, backtestStartDate, backtestEndDate, forecastDays, pastDays, maValue,
                                       stepMonth, sampleDataSize)

# 生成结果报告
resultDf = realPreDf.copy()
resultDf['ratio'] = np.insert(np.full(len(realPreDf)-1, np.nan), 0, ratio)

# 保存结果报告
resultDf.to_csv(resultDfFile, encoding='utf-8')



