import pandas as pd
from itertools import product
from tqdm import tqdm


def calMACD(df, lowShortEMASpan, highShortEMASpan, lowLongEMASpan, highLongEMASpan, lowDEASpan, highDEASpan):
    for shortEMASpan, longEMASpan, DEASpan in tqdm(
            product(range(lowShortEMASpan, highShortEMASpan + 1),
                range(lowLongEMASpan, highLongEMASpan + 1),
                range(lowDEASpan, highDEASpan + 1))):
        DIFName = "DIF({},{})".format(shortEMASpan, longEMASpan)
        DEAName = "DEA({},{},{})".format(shortEMASpan, longEMASpan, DEASpan)
        df[DIFName] = df['Close'].ewm(span=shortEMASpan, adjust=False).mean() - df['Close'].ewm(
            span=longEMASpan, adjust=False).mean()
        df[DEAName] = df[DIFName].ewm(span=DEASpan, adjust=False).mean()

    return df


stockDataFile = r'./StockData.xlsx'
MACDFile = r'./MACD1.csv'

df = pd.read_excel(stockDataFile, index_col='Date', parse_dates=['Date'])[['Open', 'Close']]

MACDdf = calMACD(df, 1, 15, 20, 50, 5, 15)

MACDdf.to_csv(MACDFile)
