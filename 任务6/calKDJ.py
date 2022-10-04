import pandas as pd

stockDataFile = r"./stockData.xlsx"
KDJFile = r"./KDJ.csv"

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])
KDJDf = df.copy()[['Open', 'Close']]

lowList = df['Low'].rolling(9).min()  # 计算low值9日移动最低
highList = df['High'].rolling(9).max()  # 计算high值9日移动最高
closeList = df['Close']  # 收盘价

RSVList = (closeList - lowList) / (highList - lowList) * 100  # 计算RSV(未成熟随机值)
KDJDf['K'] = RSVList.ewm(alpha=(1 / 3), adjust=False).mean()  # 计算K值
KDJDf['D'] = KDJDf['K'].ewm(alpha=(1 / 3), adjust=False).mean()  # 计算D值
KDJDf['J'] = 3.0 * KDJDf['K'] - 2.0 * KDJDf['D']  # 计算J值

KDJDf.to_csv(KDJFile)
