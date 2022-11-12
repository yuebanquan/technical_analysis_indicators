import pandas as pd
import numpy as np
import datetime
import lRPredict

# 数据集路径
stockDataFile = r"./StockData.xlsx"
iterAllDfFile = r'./result/iterAllDf_2_3.xlsx'
bestResultDfFile = r'./result/bestResult_2_3.csv'

# 样本内区间
sampleStartDate = datetime.datetime.strptime('2005-1-4', '%Y-%m-%d')
sampleEndDate = datetime.datetime.strptime('2013-12-31', '%Y-%m-%d')
# 样本外区间
backtestStartDate = datetime.datetime.strptime('2014-01-02', '%Y-%m-%d')
backtestEndDate = datetime.datetime.strptime('2022-9-30', '%Y-%m-%d')

# 参数
forecastDays = 2  # 预测未来第几天的股价
pastDaysRange = range(1, 11)  # 过去n日作为一组
maRange = range(2, 61)  # MA取值
stepMonth = 3  # 滑动窗口步长,月
sampleDataSize = 9  # 样本内数据量: 9年

df = pd.read_excel(stockDataFile, sheet_name='sz50', index_col='Date', parse_dates=['Date'])  # 读取数据集

iterAll = []
for pastDays in pastDaysRange:
    for maValue in maRange:
        realPreDf, ratio = lRPredict.lRPredict(df, backtestStartDate, backtestEndDate, forecastDays, pastDays, maValue,
                                               stepMonth, sampleDataSize)
        iterAll.append([pastDays, maValue, ratio])
        print(f'pastDays = {pastDays}, ma = {maValue}, ratio={ratio}', end='\r')
iterAllDf = pd.DataFrame(iterAll, columns=['pastDays', 'ma', 'ratio'])
iterAllDf.to_csv(iterAllDfFile, encoding='utf-8-sig', index=False)

# 找最佳
bestId = iterAllDf['ratio'].idxmin()
bestPastDays = iterAllDf.loc[bestId, 'pastDays']
bestMa = iterAllDf.loc[bestId, 'ma']
bestRealPreDf, bestRatio = lRPredict.lRPredict(df, backtestStartDate, backtestEndDate, forecastDays, bestPastDays,
                                               bestMa, stepMonth, sampleDataSize)

# 生成结果报告
bestResult = bestRealPreDf.copy()
bestResult['bestPastDays'] = np.insert(np.full(len(bestRealPreDf) - 1, np.nan), 0, bestPastDays)
bestResult['bestMa'] = np.insert(np.full(len(bestRealPreDf) - 1, np.nan), 0, bestMa)
bestResult['ratio'] = np.insert(np.full(len(bestRealPreDf) - 1, np.nan), 0, bestRatio)

# 保存结果报告
iterAllDf.to_excel(iterAllDfFile, index=False)
bestResult.to_csv(bestResultDfFile, encoding='utf-8')