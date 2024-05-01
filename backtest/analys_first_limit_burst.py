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

global_wait_seconds = 3
# 指定回测年份
year = 2024
#交易日期
dates = []
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_today_strongest.json', 'r',) as file:
        strongest_stocks_data = json.load(file)
except FileNotFoundError:
    strongest_stocks_data = []

for item in stocks_data:
    dates.append(item['date'])
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_burst_data.json', 'r',) as file:
        burst_stocks_data = json.load(file)
except FileNotFoundError:
    burst_stocks_data = []

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_burst_filter.json', 'r',) as file:
        burst_filter_stocks_data = json.load(file)
except FileNotFoundError:
    burst_filter_stocks_data = []

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

# def getBurstTime(date,code):
#     global burst_stocks_data
#     for item in burst_stocks_data:
#         if date == item['date']:
#             for item2 in item['data']:
#                 if item2['code'] == code:
#                     return item2['first_time_limit']
#     return ''

def isInStocks(code, stocks):
    for item in stocks:
        if code == item['code']:
            return True
    return False

def isInStrongest(date,code):
    global strongest_stocks_data
    for item in strongest_stocks_data:
        if date == item['date']:
            for item2 in item['data']:
                if item2['code'] == code:
                    return True
    return False

#从一板中统计炸板的数据
# data = []
# for item in today_data_list:
#     burstStocks = []
#     for item2 in item['data']:
#         burstTime = getBurstTime(item['date'],item2['code'])
#         if burstTime:
#             item2['first_time_limit'] = burstTime
#             burstStocks.append(item2)
#     data.append({'date':item['date'],'data':burstStocks})
# with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_burst_filter.json', 'w') as file:
#      json.dump(data, file,ensure_ascii=False,  indent=4) 

# for item in dates[len(burst_stocks_data):]:
#     stocks = []
#     # 导航到搜索页面
#     browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={item}主板非st炸板&querytype=stock")
#     # 等待页面加载
#     browserTab.wait(global_wait_seconds)
#     result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
#     soup = BeautifulSoup(result['result']['value'], 'html.parser')
#     # 找到所有的<tr>标签，每个<tr>表示一行数据
#     rows = soup.find_all('tr')
#     # 遍历每一行，提取需要的信息
#     for row in rows:
#         cells = row.find_all('td')  # 在每行中找到所有的<td>单元格
#         if len(cells) >= 6:  # 确保单元格数量足够
#             stock_code = cells[2].text.strip()  # 股票代码
#             stock_name = cells[3].text.strip()  # 股票名称
#             first_time_limit = cells[6].text.strip()  # 首次涨停时间
#             stocks.append({'date':item,'code':stock_code,'name':stock_name,'first_time_limit':first_time_limit})
#     burst_stocks_data.append({'date':item,'data':stocks})   
#     with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_burst_data.json', 'w') as file:
#                 json.dump(burst_stocks_data, file,ensure_ascii=False,  indent=4) 

filter_strongest_stocks_data = []
for item in strongest_stocks_data:
    data = []
    for item2 in item['data']:
        if float(item2["current_opening_increase"]) < 8:
            data.append(item2)
    filter_strongest_stocks_data.append({'date':item['date'],'data':data})
burstRatio = []
burstRatioStocks = []
#统计一板封板率
# for item in burst_filter_stocks_data:
#     for item2 in stocks_data:
#         if item['date'] == item2['date']:
#             count = 0
#             for item3 in item2['data']:
#                 if item3['limit'] == 2:
#                     count += 1
#     if (len(item['data'])+count) != 0:
#         burstRatio.append(len(item['data'])/(len(item['data'])+count))

# 采用筛选策略后纠正一板封板率,通过策略筛选，炸板率从28%下降到24%

for item in filter_strongest_stocks_data:
     cuccessCount = 0
     burstCount = 0
     successStocks = []
     burstStocks = []
     for item2 in stocks_data:
        if item['date'] == item2['date']:
            for item3 in item2['data']:
                if item3['limit'] == 2 and isInStocks(item3['code'],item['data']):
                    cuccessCount += 1
                    successStocks.append(item3)
     for item3 in burst_filter_stocks_data:
        if item['date'] == item3['date']:
            for item4 in item3['data']:
                if isInStocks(item4['code'],item['data']):
                    burstCount += 1
                    burstStocks.append(item4)
     if cuccessCount+burstCount != 0:
        burstRatio.append(burstCount/(cuccessCount+burstCount))
        burstRatioStocks.append({'state':item['date'],'success':successStocks,'burst':burstStocks})
        # with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_burst_ratio_data.json', 'w') as file:
        #     json.dump(burstRatioStocks, file,ensure_ascii=False,  indent=4) 

# print(burstRatio)

# for item in burst_filter_stocks_data:
#     for item2 in stocks_data:
#         if item['date'] == item2['date']:
#             count = 0
#             for item3 in item2['data']:
#                 if item3['limit'] == 2:
#                     count += 1
#     oringinCount = len(item['data'])
#     for item4 in item['data']:
#         if not isInStrongest(item['date'],item4['code']):
#             oringinCount -= 1

#     if (oringinCount+count) != 0:
#         burstRatio.append(oringinCount/(oringinCount+count))

#算上一字板一进二自然炸板率为28%
count = 0
for item in burstRatio:
    count += item
print(round(count/len(burstRatio),2))

#计算总数量
# count = 0
# for item in burst_filter_stocks_data:
#     for item2 in item['data']:
#         count += 1
# print(count)