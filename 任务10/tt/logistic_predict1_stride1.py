import math

import pandas as pd
import numpy as np
import time
import datetime
import talib
import copy
from sklearn.linear_model import LinearRegression


def process_train_data(start_time, end_time, stock_data):
    stock_data['MA_1'] = talib.MA(stock_data["close"].values, 30)
    stock_data = stock_data[(stock_data['date'] >= start_time)].reset_index(drop=True)
    stock_data = stock_data[(stock_data['date'] <= end_time)].reset_index(drop=True)
    stock_data1 = stock_data
    stock_data = np.array(stock_data.drop(columns=['date']))
    train_x = []
    train_y = []
    for i in range(0, len(stock_data)):
        if (i + 5 >= len(stock_data)):
            break
        train_x.append(stock_data[i:i + 5].reshape(1, -1)[0])
        train_y.append(stock_data[i + 5][3])
    return train_x, train_y


def process_test_data(start_time, end_time, stock_data):
    stock_data['MA_1'] = talib.MA(stock_data["close"].values, 30)
    stock_data = stock_data[(stock_data['date'] >= start_time)].reset_index(drop=True)
    stock_data = stock_data[(stock_data['date'] <= end_time)].reset_index(drop=True)
    stock_data = np.array(stock_data.drop(columns=['date']))
    test_x = []
    test_y = []
    for i in range(0, len(stock_data)):
        if (i + 5 >= len(stock_data)):
            break
        test_x.append(stock_data[i:i + 5].reshape(1, -1)[0])
        test_y.append(stock_data[i + 5][3])
    return test_x, test_y


def compute_predication_real_ratio(real_y, pre_y):
    ratio = 0
    for i in range(len(real_y)):
        ratio += math.fabs((pre_y[i] - real_y[i]) / real_y[i])
    ratio = ratio / float(len(real_y))
    return ratio


def logistic_predict(trade_date, original_stock_data):
    real_y = []
    pre_y = []
    for i in range(2014, 2023):
        end_month = 13
        if (i == 2022):
            end_month = 10
        for j in range(1, end_month):
            ###训练数据处理
            stock_data = copy.deepcopy(original_stock_data)
            start_time_1 = datetime.date(i - 9, j, 1)
            start_time = \
                trade_date[(trade_date['calendar_date'] < str(start_time_1))].reset_index(drop=True)[-5:-4].values[0][0]
            end_time_1 = datetime.date(i, j, 1)
            end_time = \
                trade_date[(trade_date['calendar_date'] < str(end_time_1))].reset_index(drop=True)[-1:].values[0][0]
            train_x, train_y = process_train_data(start_time, end_time, stock_data)

            ###预测数据处理
            start_time_1 = datetime.date(i, j, 1)
            start_time = \
                trade_date[(trade_date['calendar_date'] < str(start_time_1))].reset_index(drop=True)[-5:-4].values[0][0]
            if (j != 12):
                end_time_1 = datetime.date(i, j + 1, 1)
                end_time = \
                    trade_date[(trade_date['calendar_date'] < str(end_time_1))].reset_index(drop=True)[-1:].values[0][0]
            else:
                end_time_1 = datetime.date(i + 1, 1, 1)
                end_time = \
                    trade_date[(trade_date['calendar_date'] < str(end_time_1))].reset_index(drop=True)[-1:].values[0][0]

            test_x, test_y = process_test_data(start_time, end_time, stock_data)
            real_y.append(test_y)
            model = LinearRegression()
            model.fit(train_x, train_y)
            pre_data = model.predict(test_x)
            pre_y.append(list(pre_data))

    real_y = np.array(sum(real_y, []))
    pre_y = np.array(sum(pre_y, []))
    ratio = compute_predication_real_ratio(real_y, pre_y)
    result_dataframe = pd.DataFrame(list(zip(real_y, pre_y)), columns=["real", "pre"])
    result_dataframe = pd.concat([result_dataframe, pd.DataFrame([ratio], columns=["实际值与预测值差距比"])], axis=1)
    result_dataframe.to_csv("task-10-stride1-pre1.csv", index=False, encoding='UTF-8')


if __name__ == '__main__':
    trade_date = pd.read_csv("data/trade_date.csv", encoding="gbk")
    trade_date = trade_date[(trade_date['is_trading_day'] == 1)].reset_index(drop=True)
    stock_data = pd.read_excel("data/StockData.xlsx", sheet_name='sz50').rename(
        columns={'Date': 'date', "Open": "open", "Close": 'close'})
    stock_data["date"] = pd.to_datetime(stock_data["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    logistic_predict(trade_date, stock_data)
