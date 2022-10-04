
def getFirstDate(df, year):
    """
    获取某年第一个交易日
    
    Parameters
    ----------
    df : Dataframe
        股票数据.
    year : int/str
        年份.

    Returns
    -------
    firstDate : str
        该年第一个交易日.

    """
    # 如果传入年份为整型，转换为字符串
    if type(year) == int:
        year = str(year)
    
    # 计算第一个交易日
    firstDate = df.loc[year].iloc[0].name.strftime('%Y-%m-%d')
    
    return firstDate


def getLastDate(df, year):
    """
    获取某年最后一个交易日

    Parameters
    ----------
    df : DataFrame
        股票数据.
    year : TYPE
        年份.

    Returns
    -------
    lastDate : str
        该年最后一个交易日.

    """
    # 如果传入年份为整型，转换为字符串
    if type(year) == int:
        year = str(year)
    
    # 计算最后一个交易日
    lastDate = df.loc[year].iloc[-1].name.strftime('%Y-%m-%d')
    
    return lastDate


def getPreDate(df, date):
    """
    获取前一个交易日
    
    Parameters
    ----------
    df : DataFrame
        股票数据.
    date : str
        日期.
    
    Returns
    -------
    lastDate : str
        该年最后一个交易日.
    """
    # 计算最后一个交易日
    preDate = df.loc[date::-1].iloc[1].name.strftime('%Y-%m-%d')
    
    return preDate



# =============================================================================
# saveFile = r"./StockData.xlsx"     # 数据保存路径
# # 读取沪深300指数的开盘价、收盘价，并将日期作为索引
# df = pd.read_excel(saveFile, index_col='Date',  parse_dates=['Date'])[['Open', 'Close']]
# 
# 
# getLastDate(df, 2006)
# =============================================================================

