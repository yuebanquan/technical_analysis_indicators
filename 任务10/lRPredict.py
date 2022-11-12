import pandas as pd
import numpy as np
import datetime
import dateutil.relativedelta
from sklearn.linear_model import LinearRegression


def getStockDataDf(df, maValue):
    """
    计算股票数据,增加均值列
    :param df:
    :param maValue:
    :return:
    """
    stockDataDf = df.copy()  # 深拷贝
    stockDataDf['Ma'] = df.Close.rolling(maValue).mean()  # 计算MA
    return stockDataDf





def getSlidingWindowDf(stockDataDf, sampleDataSize, backtestStartDate, backtestEndDate, stepMonth):
    """
    通过样本内数据量, 滑动窗口步长求滑动窗口
    :param stockDataDf: 股票数据
    :param sampleDataSize: 样本内数据量: 9年
    :param stepMonth: 滑动窗口步长,月
    :return: 滑动窗口Df
    """
    # 计算每个窗口
    slidingWindowBacktestStartDateList = []  # List, 存每个窗口样本外开始日期
    slidingWindowBacktestEndDateList = []  # List, 存每个窗口样本外结束日期
    delta = backtestStartDate  # 循环控制条件
    while (delta < backtestEndDate):  # 以相应步长遍历样本外区间
        # 计算窗口样本外开始日期
        startDate = stockDataDf.loc[delta.strftime('%Y-%m')].index[0]  # 该窗口的样本外开始日期:这个月的第一个交易日
        slidingWindowBacktestStartDateList.append(startDate)  # 加入List中

        # 计算窗口样本外结束日期
        try:

            endYearMonth = (delta + dateutil.relativedelta.relativedelta(months=stepMonth - 1)) \
                .strftime('%Y-%m')  # (开始日期 + 步长 - 1)的年月
            endDate = stockDataDf.loc[endYearMonth].tail(1).index[0]  # 该窗口的样本外结束日期:(开始日期 + 步长 - 1)的月份最后一天
            slidingWindowBacktestEndDateList.append(endDate)  # 加入List中
        except Exception as e:
            # 抛出异常, 说明最后一个窗口不满步长, 该窗口样本内外结束日期为样本外结束日期
            slidingWindowBacktestEndDateList.append(backtestEndDate)

        delta = delta + dateutil.relativedelta.relativedelta(months=stepMonth)  # 循环控制条件增加相应步长

    # 构建滑动窗口Df
    slidingWindowDf = pd.DataFrame(
        data={'样本内数据年份数': sampleDataSize, '步长/月': stepMonth,
              '样本外开始': slidingWindowBacktestStartDateList, '样本外结束': slidingWindowBacktestEndDateList},
        columns=['样本内数据年份数', '步长/月',
                 '样本内开始', '样本内结束',
                 '样本外开始', '样本外结束'])

    slidingWindowDf['样本内开始'] = slidingWindowDf['样本外开始'].apply(
        lambda x:
        stockDataDf.loc[(x - dateutil.relativedelta.relativedelta(years=sampleDataSize)).strftime('%Y-%m')].index[0]
    )  # 样本内开始 = (样本外开始 - 步长)那个月的第一个交易日

    slidingWindowDf['样本内结束'] = slidingWindowDf['样本外开始'].apply(
        lambda x:
        stockDataDf.loc[(x - dateutil.relativedelta.relativedelta(months=1)).strftime('%Y-%m')].tail(1).index[0]
    )  # 样本内结束 = 样本外开始那个月的上一个月的最后一个交易日

    return slidingWindowDf


def getTrainData(stockDataDf, trainStartDate, trainEndDate, forecastDays, pastDays):
    """
    计算该窗口的训练数据集
    :param stockDataDf: 股票数据
    :param trainStartDate: 该窗口的训练开始时间
    :param trainEndDate: 该窗口的训练结束时间
    :param pastDays: 将pastDays行压成一行作为一个trainX
    :return: trainX, trainY
    """
    trainX = []  # 训练数据集X
    trainY = []  # 训练数据集Y
    swStockDataDf = stockDataDf[trainStartDate:trainEndDate]  # 取当前滑动窗口股票数据, 深拷贝
    swStockData = np.array(swStockDataDf)  # 当前滑动窗口训练数据集, 二维数组
    for i in range(len(swStockData)):  # 根据将过去pastDays天数据作为一组
        if (i + pastDays + (forecastDays - 1) >= len(swStockData)):  # 最后一组不满pastDays, 丢弃
            break
        trainX.append(swStockData[i:i + pastDays].reshape(1, -1)[0])  # 将pastDays行压缩成一行作为trainX的一组
        trainY.append(swStockData[i + pastDays + (forecastDays - 1)][3])  # 将第pastDays天的收盘价作为trainY
    return trainX, trainY


def getTestData(stockDataDf, testStartDate, testEndDate, forecastDays, pastDays):
    """
    计算该窗口的测试集
    :param stockDataDf: 股票数据
    :param testStartDate: 该窗口的测试开始时间
    :param testEndDate: 该窗口的测试结束时间
    :param pastDays: 将pastDays行压成一行作为一个testX
    :return: testX, testY
    """
    testX = []  # 测试集X
    testY = stockDataDf[testStartDate:testEndDate].Close  # 测试集Y

    swStockDataDf = stockDataDf.copy()
    swStockDataDf['numIndex'] = range(len(swStockDataDf))  # 建立数字索引

    # 将开始日期提前pastDays天, testY才能取到滑动窗口的第一天
    testStartDate = \
        swStockDataDf.query(
            f"numIndex == {(swStockDataDf.loc[testStartDate, 'numIndex'] - (pastDays + (forecastDays - 1)))}").index[0]
    # testEndDate = swStockDataDf.query(f"numIndex == {(swStockDataDf.loc[testEndDate, 'numIndex'] - pastDays)}").index[0]

    swStockDataDf = stockDataDf.loc[testStartDate:testEndDate]  # 取当前滑动窗口股票数据
    swStockData = np.array(swStockDataDf)  # 当前滑动窗口训练数据集, 二维数组
    for i in range(len(swStockData)):  # 根据将过去pastDays天数据作为一组
        if (i + pastDays + (forecastDays - 1) >= len(swStockData)):  # 最后一组不满pastDays, 丢弃
            break
        testX.append(swStockData[i:i + pastDays].reshape(1, -1)[0])  # 将pastDays行压缩成一行作为testX的一组
        # testY.append(swStockData[i + pastDays][3])  # 将第pastDays天的收盘价作为testY
    return testX, testY


def getRatio(realPreDf):
    ratio = (np.abs(realPreDf.real.values - realPreDf.predict.values) / realPreDf.real.values).mean()
    return ratio


def lRPredict(df, backtestStartDate, backtestEndDate, forecastDays, pastDays, maValue, stepMonth, sampleDataSize):
    stockDataDf = getStockDataDf(df, maValue)  # 计算ma列, 获得股票数据
    slidingWindowDf = getSlidingWindowDf(stockDataDf, sampleDataSize, backtestStartDate, backtestEndDate,
                                         stepMonth)  # 求滑动窗口

    # 生成zip,用于遍历滑动窗口
    swZip = zip(slidingWindowDf['样本内开始'].values, slidingWindowDf['样本内结束'].values,
                slidingWindowDf['样本外开始'].values,
                slidingWindowDf['样本外结束'].values)

    realY = pd.Series([], dtype='float64')
    predictY = []
    # 遍历每个滑动窗口
    for sw in swZip:
        # 1. 计算训练数据集trainX, trainY
        trainStartDate = sw[0]  # 当前窗口数据集开始时间
        trainEndDate = sw[1]  # 当窗口数据集结束时间
        trainX, trainY = getTrainData(stockDataDf, trainStartDate, trainEndDate, forecastDays,
                                      pastDays)  # 计算训练数据集trainX, trainY

        # 2. 计算测试集testX, testY
        testStartDate = sw[2]  # 当前窗口测试集开始时间
        testEndDate = sw[3]  # 当前窗口测试集结束时间
        testX, testY = getTestData(stockDataDf, testStartDate, testEndDate, forecastDays, pastDays)

        # 3. 训练
        model = LinearRegression()  # 设定模型为线性回归
        model.fit(trainX, trainY)  # 将数据集输入, 得到模型
        predictY.append(list(model.predict(testX)))  # 通过模型输入testX进行预测, 得到预测数据
        realY = pd.concat([realY, testY], axis=0, ignore_index=False)  # 将真实值拼接起来

    predictY = sum(predictY, [])  # 将预测值转为一维数组
    realPreDf = pd.DataFrame({'real': realY, 'predict': predictY})
    ratio = getRatio(realPreDf)

    return realPreDf, ratio
