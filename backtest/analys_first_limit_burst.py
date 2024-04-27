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

def isBurst(date,code):
    global burst_stocks_data
    for item in burst_stocks_data:
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
#         if isBurst(item['date'],item2['code']):
#             burstStocks.append(item2)
#     data.append({'date':item['date'],'data':burstStocks})

#生成炸板数据
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

burstRatio = []
#统计一板封板率

for item in burst_filter_stocks_data:
    for item2 in stocks_data:
        if item['date'] == item2['date']:
            count = 0
            for item3 in item2['data']:
                if item3['limit'] == 2:
                    count += 1
    if (len(item['data'])+count) != 0:
        burstRatio.append(len(item['data'])/(len(item['data'])+count))

#一板炸板率为28%
count = 0
for item in burstRatio:
    count += item
print(round(count/len(burstRatio),2))