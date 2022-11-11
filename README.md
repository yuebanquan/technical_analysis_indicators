# Technical-analysis-indicators
## 项目目的
使用技术面指标分析沪深 300、上证 50 等指数，进⾏策略构建
## 环境
1. python 3.9
2. numpy 1.23.4
3. pandas 1.5.0
4. matplotlib 3.6.1
## 简介
### 任务1: 单均线(MA)策略
1. 第一步：对沪深300指数（399300）进行如下操作：
   统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。
   做多：
   如果当日收盘价大于240日均线，第二日以开盘价买入；
   如果当日收盘价小于240日均线，第二日以开盘价卖出。
2. 第二步：在第一步的基础上，找最佳长期均线（120--240）。
3. 第三步：样本内区间2006-1-4至2013-12-31，找最佳长期均线（120--240）；样本外区间2014-1-2至2021-12-31 ，执行该策略。
4. 第四步：初始样本内区间2006-1-4至2013-12-31，找最佳长期均线（120--240）；样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式（每次滑动1年）运行，即用过去8年的数据找最佳长期均线，在下1年执行该策略。
### 任务2: 双均(MA)策略
1. 第一步：对沪深300指数（399300）进行如下操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。
做多：
如果5日均线向上穿过20日均线，第二日以开盘价买入；
如果5日均线向下穿过20日均线，第二日以开盘价卖出。
2. 第二步：在第一步的基础上，找最佳短期（1-15）和中期均线（20-100）的组合。
3. 第三步：样本内区间2006-1-4至2013-12-31，找最佳短期（1-15）和中期均线（20-100）的组合；样本外区间2014-1-2至2021-12-31 ，执行该策略。
4. 第四步：是第三步的推广，完整描述整个要求如下：
对沪深300指数（399300）进行如下操作，统计结果（ 手续费万分之五，初始资金100万）。
初始样本内区间2006-1-4至2013-12-31，找最佳短期（1-15）和中期均线（20-100）的组合；样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式，执行该策略。
做多：
如果短期均线向上穿过中期均线，第二日以开盘价买入；
如果短期均线向下穿过中期均线，第二日以开盘价卖出。
### 任务3: 三均线(MA)策略
1. 第一步：对沪深300指数（399300）进行如下操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。
  股价上穿长期均线，并且短期均线在中期均线之上，开仓买入。
  股价在长期均线之上，如果短期均线向下穿过中期均线，第二日以开盘价卖出；
  股价在长期均线之上，如果短期均线向上穿过中期均线，第二日以开盘价买入。
  股价下穿长期均线，平仓卖出。
  找最佳长期（120-180）、中期（5-21）、短期（1-8）的组合。
2. 第二步：样本内区间2006-1-4至2013-12-31，找最佳短期和中期均线、长期均线的组合；
  样本外区间2014-1-2至2021-12-31 ，执行该策略。
3. 第三步：按照滑动窗口方式，执行第二步策略
4. 第四步：在第三步的基础上，样本内区间设置为1-7年。样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式，执行该策略。
### 任务4: EMA策略
1. 对沪深300指数（399300）进行如下操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。
做多，找最佳长期EMA（120--240）：
如果当日收盘价大于长期EMA，第二日以开盘价买入；
如果当日收盘价小于长期EMA，第二日以开盘价卖出。
2. 对沪深300指数（399300）进行如下操作，统计结果（ 手续费万分之五，初始资金100万）。
初始样本内区间2006-1-4至2013-12-31，找最佳短期EMA（1-15）和中期EMA（20-100）的组合；样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式，执行该策略。
做多：如果短期EMA向上穿过中期EMA，第二日以开盘价买入；如果短期EMA向下穿过中期EMA，第二日以开盘价卖出。
3. 类似任务三的第四步。
### 任务5: MACD策略
五、用MACD指标完成以下任务。尽量自己编程计算MACD。
1. 对沪深300指数（399300）进行如下操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。
做多：
如果DIF向上穿过DEA，第二日以开盘价买入；
如果DIF向下穿过DEA，第二日以开盘价卖出。
思考：如何根据MACD指标的特点，改进交易策略。
2. 对沪深300指数（399300）进行如下操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。找最佳买入DEA1（-100至100）和卖出DEA2（-100至100）的组合。
做多：
如果DEA<DEA1，并且DIF向上穿过DEA，第二日以开盘价买入；
如果DEA>DEA2，并且DIF向下穿过DEA，第二日以开盘价卖出。
3. 对沪深300指数（399300）进行如下操作，统计结果（ 手续费万分之五，初始资金100万）。
初始样本内区间2006-1-4至2013-12-31，找最佳买入DEA1（-100至100）和卖出DEA2（-100至100）的组合；样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式，执行该策略。
做多：
如果DEA<DEA1，并且DIF向上穿过DEA，第二日以开盘价买入；
如果DEA>DEA2，并且DIF向下穿过DEA，第二日以开盘价卖出。
### 任务6: KDJ策略
1. 步骤1：
   * 1a: 对沪深300指数（399300）进行如下操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。
        找最佳买入D1（10至90）和卖出D2（20至100）的组合。
        做多：如果D<D1，并且K向上穿过D，第二日以开盘价买入；如果D>D2，并且K向下穿过D，第二日以开盘价卖出。
   * 1b: 找最佳买入J1（10至90）和卖出J2（30至110）的组合；
        做多：如果J<J1，并且连续1天下降然后开始上升，第二日以开盘价买入；如果J>J2，并且连续1天上升然后开始下降，第二日以开盘价卖出。
   * 1c: 找最佳买入J1（10至90）和卖出J2（30至110）的组合；
        做多：如果J<J1，并且连续2天下降然后开始上升，第二日以开盘价买入；如果J>J2，并且连续2天上升然后开始下降，第二日以开盘价卖出。
2. 对沪深300指数（399300）进行如下操作，统计结果（ 手续费万分之五，初始资金100万）。初始样本内区间2006-1-4至2013-12-31，样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式，执行该策略。
   2a、2b、2c分别与1a、1b、1c要求相同。
### 任务7: 计算年均收益率（复利）、每日净资产、每年收益率（转换为年化收益率）、最大回测率、夏普率，画出每日净资产涨跌幅与标的涨跌幅对照图
重新计算任务1-4、2-4、3-3、4-3、5-3中采用滑动窗口方式的步骤，初始样本内区间2006-1-4至2013-12-31，样本外区间2014-1-2至2021-12-31，样本内年份数都是8年。
最后的结果要求计算年均收益率（复利）、每日净资产、每年收益率（转换为年化收益率）、最大回测率、夏普率，画出每日净资产涨跌幅与标的涨跌幅对照图。
### 任务8: 综合指标
1. 对沪深300指数（399300）进行操作，统计结果（手续费万分之五，初始资金100万），交易区间2006-1-4至2021-12-31 。找最佳参数组合。
2. 对沪深300指数（399300）进行操作，统计结果（手续费万分之五，初始资金100万）。
初始样本内区间2006-1-4至2013-12-31，找最佳参数组合；样本外区间2014-1-2至2021-12-31 ，按照滑动窗口方式，执行该策略。
3. 对上证50指数（000016）进行同步骤1操作。交易区间从2005-1-4开始；样本外区间2014-1-2至2021-12-31。
4. 对上证50指数（000016）进行同步骤2操作。交易区间从2005-1-4开始；样本外区间2014-1-2至2021-12-31。
### 任务9: 更新滑动窗口功能
滑动窗口步长修改为1月、3月、6月，对上证50指数，做任务二的第四步。
第三步：
样本内区间2005-1-4至2013-12-31，找最佳短期（1-15）和中期均线（20-100）的组合；
样本外区间2014-1-2至2022-9-30 ，
以滑动窗口方式（步长分别为1月、3月、6月）执行该策略。
只要计算年均复利，不必计算夏普率等。
有4处修改：
1. “做任务二的第四步”，原来写的第三步不准确，滑动窗口方式是第四步。
2.  样本内区间起始日期是2005-1-4，提前了1年，所以样本内的数据量从8年变更为9年。
3.  结束日期是2022-9-30，新增了9个月的数据。
4.  只要计算年均复利，不必计算夏普率等。
### 任务10: 线性回归预测
对上证50指数（000016）进行价格预测，预测未来1日、2日、5日的股价；采用滑动窗口方式（步长分别为1月、3月、6月）。
输入：过去n日的开盘价、最高价、最低价、收盘价、成交量、n日均线等等。
方法：线性预测。
