# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import Utils


stockDataFile = r'./StockData.xlsx'
startDate = '2006-01-04'
endDate = '2021-12-31'

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]
tradingDf = df[startDate:endDate].copy()
tradingDf['sign'] = np.nan

# 计算ma5和ma20
ma5 = 
ma20 = df['Close'].rolling(20).mean()

# 计算金叉、死叉
s1 = ma5 < ma20
s2 = ma5 > ma20
deathCross = s1 & s2.shift(1)
goldenCross = ~(s1 | s2.shift(1))


# 计算交易信号
startOrEndSign = 0  # 初始/结束信号
buySign = 1         # 买入信号
sellSign = -1       # 卖出信号


# 金叉第二日买入，死叉第二日卖出
buyDate = goldenCross.shift(1)[startDate:endDate]   # 买入日期
sellDate = deathCross.shift(1)[startDate:endDate]   # 卖出日期
tradingDf.loc[buyDate, 'sign'] = buySign            # 写入买入信号
tradingDf.loc[sellDate, 'sign'] = sellSign          # 写入卖出信号

# 判断第一个交易日是否买入
preStartDate = Utils.getPreDate(df, startDate)
if ma5[preStartDate] >= ma20[preStartDate]:
    tradingDf.loc[startDate, 'sign'] = buySign
else:
    tradingDf.loc[startDate, 'sign'] = startOrEndSign

tradingDf = tradingDf.dropna(subset=['sign'])
