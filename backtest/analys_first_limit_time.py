#找出指定日期资金流入最强个股
import os
import re
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
from  utils.judgeBurst import judgeBurst
import pychrome
import math
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt

global_wait_seconds = 3
# 指定回测年份
year = 2024
#交易日期
dates = []
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_today_increase.json', 'r',) as file:
        today_data_list = json.load(file)
except FileNotFoundError:
    today_data_list = []

def isEarly(first_limit_time, compared_time):
    # 将字符串转换为时间对象
    first_limit_datetime = datetime.strptime(first_limit_time, '%H:%M:%S')
    compared_datetime = datetime.strptime(compared_time, '%H:%M:%S')
    # 比较时间
    return first_limit_datetime <= compared_datetime

def isFirstBurstTime(date,code,burst_time):
    for item in stocks_data:
        if item['date'] == date:
            for item2 in item['data']:
                if item2['limit'] == 2 and isEarly(item2['first_limit_time'],burst_time):
                    return ''
    return burst_time


def getBurstTime(date,code):
    global burst_stocks_data
    for item in burst_stocks_data:
        if date == item['date']:
            for item2 in item['data']:
                if item2['code'] == code and item2['first_time_limit']!='09:30:00' and isFirstBurstTime(date,code,item2['first_time_limit']):
                    return item2['first_time_limit']
    return ''

def isInStrongest(date,code):
    global strongest_stocks_data
    for item in strongest_stocks_data:
        if date == item['date']:
            for item2 in item['data']:
                if item2['code'] == code:
                    return True
    return False

stocks = []
for item in stocks_data:
    data = {'date':item['date'],'data':[]}
    for item3 in item['data']:
        if item3['limit'] == 2:
            for item2 in today_data_list:
                if item2['date'] == item['date']:
                    for item4 in item2['data']:
                        if item4['code'] == item3['code']:
                            item3['next_bidding_increase'] =  item4['next_bidding_increase']
                            data['data'].append(item3)
    stocks.append(data)
# with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_first_limit_time.json', 'w') as file:
#      json.dump(stocks, file,ensure_ascii=False,  indent=4) 


#计算总数量
# count = 0
# for item in stocks:
#     for item2 in item['data']:
#         count += 1
# print(count)

increaseArr = []
count1 = 0
count2 = 0
flag = 8
for item in stocks:
    for item2 in item['data']:
        increaseArr.append(float(item2['next_bidding_increase'].strip('%')))
# print(increaseArr)
for item3 in increaseArr:
    if item3 > flag:
        count1 += 1
    else:
        count2 += 1
print(f'{count1/count2}')
# 给定的数据
data = np.array(increaseArr)

# 设置直方图的边界
bins = np.linspace(-10, 10, 21)  # 创建20个等间距的区间

# 计算直方图
hist, bin_edges = np.histogram(data, bins=bins)

# 绘制直方图
# plt.figure(figsize=(8, 4))
# plt.hist(data, bins=bins, alpha=0.75, color='blue', edgecolor='black')
# plt.title('数据分布频率')
# plt.xlabel('数值区间')
# plt.ylabel('频率')
# plt.grid(True)
# plt.show()