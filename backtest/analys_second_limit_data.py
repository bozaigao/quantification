import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
import pychrome
import math
import matplotlib.pyplot as plt
import numpy as np
import re
year = 2024

try:
    with open(f'{os.getcwd()}/backtest/{year}_second_limit_analys.json', 'r') as file:
        dragon_data = json.load(file)
except FileNotFoundError:
    dragon_data = []

#分析热度分布情况
# ranks = []
# for item in dragon_data:
#     for item2 in item['data']:
#         ranks.append(int(item2['rank']))

# # 使用numpy的histogram函数计算直方图的数据
# # bins参数定义了数据分区的方式，这里例如我们将数据分为10个区间
# hist, bin_edges = np.histogram(ranks, bins=10)
# # 打印每个区间的频率
# print("Bin edges:", bin_edges)
# print("Histogram counts:", hist)
# # 绘制直方图
# plt.figure()
# plt.hist(ranks, bins=10, alpha=0.75, color='blue', edgecolor='black')
# plt.title('Rank Distribution')
# plt.xlabel('Rank')
# plt.ylabel('Frequency')
# plt.show()

 
# 分析涨停时间分布
# times = ["13:29:05", "09:30:00", "14:05:30", "10:15:25", "13:45:10", "11:00:00"]

# # 将时间字符串转换为datetime.time对象
# time_objects = [datetime.strptime(time_str, "%H:%M:%S").time() for time_str in times]

# # 将时间转换为从午夜开始的分钟数
# minutes = [time.hour * 60 + time.minute for time in time_objects]

# # 定义时间区间（bins），假设交易时间从9:30到15:00
# bins = range(570, 901, 30)  # 从570分钟(9:30)开始，每30分钟一个区间，直到900分钟(15:00)

# # 绘制直方图
# plt.figure(figsize=(10, 5))
# plt.hist(minutes, bins=bins, alpha=0.75, color='blue', edgecolor='black')
# plt.title('First Limit Time Distribution')
# plt.xlabel('Time of Day')
# plt.ylabel('Frequency of First Limit Events')
# plt.xticks(bins, [datetime.strptime(str(x), "%M").strftime("%H:%M") for x in bins], rotation=45)
# plt.grid(True)
# plt.show()

# # 如果你需要精确的分布数据
# hist, bin_edges = np.histogram(minutes, bins=bins)
# print("Bin edges:", [datetime.strptime(str(int(edge)), "%M").strftime("%H:%M") for edge in bin_edges])
# print("Histogram counts:", hist)

#统计首板次日涨幅分布
# 示例数据，包含bidding_increase字段的百分比值
# bidding_increases = []
# for item in dragon_data:
#     for item2 in item['data']:
#         if not item2['pre_bidding_increase'] == '--%':
#            bidding_increases.append(item2['pre_bidding_increase'])

# # 将百分比字符串转换为浮点数
# increases = [float(value.strip('%')) for value in bidding_increases]

# # 计算直方图的数据
# # 可以调整bins的数量或范围以更好地适应数据
# hist, bin_edges = np.histogram(increases, bins=10)

# # 绘制直方图
# plt.figure(figsize=(10, 6))
# plt.hist(increases, bins=10, color='skyblue', edgecolor='black', alpha=0.7)
# plt.title('Distribution of Bidding Increase')
# plt.xlabel('Bidding Increase (%)')
# plt.ylabel('Frequency')
# plt.grid(True)
# plt.show()

# def convert_to_number(s):
#     # 检查是否含有'万'，如果有，则乘以10000
#     multiplier = 10000 if '万' in s else 1
#     # 移除数字中的'万'和逗号
#     s = re.sub('[万,]', '', s)
#     # 转换为浮点数并根据是否有'万'调整数值
#     return float(s) * multiplier

# #分析放量系数
# volume = []
# for item in dragon_data:
#     for item2 in item['data']:
#         if '--' not in item2["bidding_volume"] and '--' not in item2["pre_bidding_volume"]:
#             print(round(convert_to_number(item2["bidding_volume"])/convert_to_number(item2["pre_bidding_volume"]),2))
#             volume.append(round(convert_to_number(item2["bidding_volume"])/convert_to_number(item2["pre_bidding_volume"]),2))

# # 使用numpy的histogram函数计算直方图的数据
# # bins参数定义了数据分区的方式，这里例如我们将数据分为10个区间
# hist, bin_edges = np.histogram(volume, bins=10)
# # 打印每个区间的频率
# print("Bin edges:", bin_edges)
# print("Histogram counts:", hist)
# # 绘制直方图
# plt.figure()
# plt.hist(volume, bins=10, alpha=0.75, color='blue', edgecolor='black')
# plt.title('Volume Distribution')
# plt.xlabel('Volume')
# plt.ylabel('Frequency')
# plt.show()

for item in dragon_data:
    for item2 in item['data']:
        if float(item2['bidding_increase'].strip('%')) > 8 and float(item2['bidding_increase'].strip('%')) < 9.7:
            print(f'{item["date"]}-{item2["name"]}')