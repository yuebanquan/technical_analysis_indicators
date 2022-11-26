import pandas as pd
import numpy as np
import datetime
import dateutil.relativedelta
from collections import deque
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


def getStockDataDf(df, maValue, forecastDays):
    """
    计算股票数据,增加均值列
    :param df:
    :param maValue:
    :return:
    """
    stockDataDf = df.copy()  # 深拷贝
    stockDataDf['Ma'] = df.Close.rolling(maValue).mean()  # 计算MA
    stockDataDf['label'] = stockDataDf['Close'].shift(-forecastDays)  # 计算未来第几天的收盘价
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
    :param pastDays: 将pastDays行作为一个trainX
    :return: trainX, trainY
    """
    swStockDataDf = stockDataDf.copy()

    # 将开始日期提前pastDays天, trainY才能取到滑动窗口的第一天
    swStockDataDf['numIndex'] = range(len(swStockDataDf))  # 建立数字索引
    trainStartDate = \
        swStockDataDf.query(
            f"numIndex == {(swStockDataDf.loc[trainStartDate, 'numIndex'] - (pastDays + (forecastDays - 1)))}"
        ).index[0]
    swStockDataDf = swStockDataDf.drop('numIndex', axis=1)  # 删除数字索引

    swStockDataDf = swStockDataDf[trainStartDate:trainEndDate]  # 取当前滑动窗口股票数据

    trainX = []  # 训练数据集X
    trainY = []  # 训练数据集Y
    # 求trainX
    deq = deque(maxlen=pastDays)  # 设定队列, 最大长度为记忆天数
    swStockData = np.array(swStockDataDf.drop('label', axis=1))  # 当前滑动窗口训练数据集(不包括最后一列label), 二维数组
    for i in swStockData:
        deq.append(list(i))
        if len(deq) == pastDays:
            trainX.append(list(deq))

    # 求trainY
    trainY = swStockDataDf['label'].iloc[pastDays - 1:].values

    trainX = np.array(trainX)
    trainY = np.array(trainY)
    return trainX, trainY


# def getTestData(stockDataDf, testStartDate, testEndDate, forecastDays, pastDays):
#     """
#     计算该窗口的训练数据集
#     :param stockDataDf: 股票数据
#     :param testStartDate: 该窗口的训练开始时间
#     :param testEndDate: 该窗口的训练结束时间
#     :param pastDays: 将pastDays行作为一个testX
#     :return: testX, testY
#     """
#     swStockDataDf = stockDataDf.copy()
#
#     # 将开始日期提前pastDays天, testY才能取到滑动窗口的第一天
#     swStockDataDf['numIndex'] = range(len(swStockDataDf))  # 建立数字索引
#     testStartDate = \
#         swStockDataDf.query(
#             f"numIndex == {(swStockDataDf.loc[testStartDate, 'numIndex'] - (pastDays + (forecastDays - 1)))}"
#         ).index[0]
#     swStockDataDf = swStockDataDf.drop('numIndex', axis=1)  # 删除数字索引
#
#     swStockDataDf = swStockDataDf[testStartDate:testEndDate]  # 取当前滑动窗口股票数据
#
#     testX = []  # 测试集X
#     testY = []  # 测试集Y
#     # 求testX
#     deq = deque(maxlen=pastDays)  # 设定队列, 最大长度为记忆天数
#     swStockData = np.array(swStockDataDf.drop('label', axis=1))  # 当前滑动窗口训练数据集(不包括最后一列label), 二维数组
#     for i in swStockData:
#         deq.append(list(i))
#         if len(deq) == pastDays:
#             testX.append(list(deq))
#
#     # 求testY
#     testY = swStockDataDf['label'].iloc[pastDays - 1:].values[:-1]
#
#     return testX, testY


def getTestData(stockDataDf, label, testStartDate, testEndDate, forecastDays, pastDays):
    """
    计算该窗口的测试集
    :param stockDataDf: 股票数据
    :param testStartDate: 该窗口的测试开始时间
    :param testEndDate: 该窗口的测试结束时间
    :param pastDays: 将pastDays行压成一行作为一个testX
    :return: testX, testY
    """
    testX = []  # 测试集X
    testY = label.loc[testStartDate:testEndDate]  # 测试集Y
    # testY = stockDataDf[testStartDate:testEndDate].Close  # 测试集Y

    swStockDataDf = stockDataDf.copy()
    swStockDataDf['numIndex'] = range(len(swStockDataDf))  # 建立数字索引

    # 将开始日期提前pastDays天, testY才能取到滑动窗口的第一天
    testStartDate = \
        swStockDataDf.query(
            f"numIndex == {(swStockDataDf.loc[testStartDate, 'numIndex'] - (pastDays + (forecastDays - 1)))}").index[0]
    # testEndDate = swStockDataDf.query(f"numIndex == {(swStockDataDf.loc[testEndDate, 'numIndex'] - pastDays)}").index[0]

    swStockDataDf = stockDataDf.loc[testStartDate:testEndDate]  # 取当前滑动窗口股票数据
    swStockData = np.array(swStockDataDf.iloc[:, :-1])  # 当前滑动窗口训练数据集, 二维数组

    for i in range(len(swStockData)):  # 根据将过去pastDays天数据作为一组
        if (i + pastDays + (forecastDays - 1) >= len(swStockData)):  # 最后一组不满pastDays, 丢弃
            break
        testX.append(swStockData[i:i + pastDays].tolist())  # 将pastDays行组成一组

    testX = np.array(testX)
    # testY = np.array(testY)
    return testX, testY


def inverse_transform_col(scaler, y, n_col):
    '''scaler是对包含多个feature的X拟合的,y对应其中一个feature,n_col为y在X中对应的列编号.返回y的反归一化结果'''
    y = y.copy()
    y -= scaler.min_[n_col]
    y /= scaler.scale_[n_col]
    return y


def getRatio(realPreDf):
    ratio = (np.abs(realPreDf.real.values - realPreDf.predict.values) / realPreDf.real.values).mean()
    return ratio


def LSTMPredict(df, backtestStartDate, backtestEndDate, forecastDays, pastDays, maValue, stepMonth, sampleDataSize):
    stockDataDf = getStockDataDf(df, maValue, forecastDays)  # 计算ma列和label列, 获得股票数据

    # label = stockDataDf['label']
    # scaler = StandardScaler()
    # scaStockDataDf = scaler.fit_transform(stockDataDf.values)  # 标准化(不包括最后一列label)
    # scaStockDataDf = pd.DataFrame(scaStockDataDf, index=stockDataDf.index, columns=stockDataDf.columns)
    # scaStockDataDf['label'] = label
    # stockDataDf = scaStockDataDf

    label = stockDataDf['label']

    scaler = MinMaxScaler()  # 实例化
    scaler = scaler.fit(stockDataDf.values)  # fit，在这里本质是生成min(x)和max(x)
    scaStockDataDf = scaler.transform(stockDataDf.values)  # 通过接口导出结果
    scaStockDataDf = pd.DataFrame(scaStockDataDf, index=stockDataDf.index, columns=stockDataDf.columns)

    slidingWindowDf = getSlidingWindowDf(scaStockDataDf, sampleDataSize, backtestStartDate, backtestEndDate,
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
        trainX, trainY = getTrainData(scaStockDataDf, trainStartDate, trainEndDate, forecastDays,
                                      pastDays)  # 计算训练数据集trainX, trainY

        # 2. 计算测试集testX, testY
        testStartDate = sw[2]  # 当前窗口测试集开始时间
        testEndDate = sw[3]  # 当前窗口测试集结束时间
        testX, testY = getTestData(scaStockDataDf,label, testStartDate, testEndDate, forecastDays, pastDays)

        # 3. 训练
        model = Sequential()
        # 构建第一层
        model.add(LSTM(10, input_shape=trainX.shape[1:], activation='tanh', return_sequences=True))
        model.add(Dropout(0.1))  # 为防止过拟合, 删除0.1%的神经元
        # 构建第二层
        model.add(LSTM(10, activation='tanh', return_sequences=True))
        model.add(Dropout(0.1))  # 为防止过拟合, 删除0.1%的神经元
        # 构建第三层
        model.add(LSTM(10, activation='tanh'))
        model.add(Dropout(0.1))  # 为防止过拟合, 删除0.1%的神经元
        # 构建全连接层
        model.add(Dense(10, activation='tanh'))
        model.add(Dropout(0.1))  # 为防止过拟合, 删除0.1%的神经元
        # 输出层
        model.add(Dense(1))
        # 编译
        model.compile(optimizer='adam', loss='mse', metrics=['mape'])
        # 训练模型
        model.fit(trainX, trainY, batch_size=32, epochs=1, validation_data=(testX, testY))

        predictY.append(model.predict(testX).reshape(1, -1).tolist()[0])  # 通过模型输入testX进行预测, 得到预测数据
        realY = pd.concat([realY, testY], axis=0, ignore_index=False)  # 将真实值拼接起来
        break

    predictY = sum(predictY, [])  # 将预测值转为一维数组
    predictY = inverse_transform_col(scaler, predictY, 6)  # 将归一化后的结果逆转
    # realY = inverse_transform_col(scaler, realY, 3)
    realPreDf = pd.DataFrame({'real': realY, 'predict': predictY})

    ratio = getRatio(realPreDf)

    return realPreDf, ratio
