import pandas as pd

stockDataFile = r"../stockData.xlsx"

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

close = df['Close']  # 收盘价

# 计算DIF & DEA
df['DIF'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()  # DEA

df.to_csv(r"MACD.csv")