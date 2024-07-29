#计算当日最高标开盘涨幅，如果有多个最高表则平均计算
from bs4 import BeautifulSoup
import pychrome
import json
import re
from pandas_market_calendars import get_calendar
import copy

global_wait_seconds = 3
# 指定开始统计年份
year = 2021
with open(f'./full_data/{year}_stocks_data.json', 'r') as file:
        stock_data = json.load(file)
# 指定年份的日期范围
dates = []# 这里替换为你的交易日日期列表
# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()
try:
    with open(f'./full_data/{year}_opening_data.json', 'r') as file:
        opening_data = json.load(file)
except FileNotFoundError:
    opening_data = []

def generateNextData(data,date):
    for item in data:
         browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={date} '{item['code']}'竞价涨幅&querytype=stock")
         browserTab.wait(global_wait_seconds)
         result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
         soup = BeautifulSoup(result['result']['value'], 'html.parser')
         div_text = soup.find('div', class_='jgy_txt_isLayout').get_text(strip=True)
         match = re.search(r'竞价涨幅(-?\d+\.\d+%)', div_text)
         if not match:
            match = re.search(r'竞价涨幅为(-?\d+\.\d+%)', div_text)
         if match:
            percentage_text = match.group(1)
         else:
            percentage_text = '0%'
         print(percentage_text)
         item['opening_increase'] = percentage_text
         item['desc'] = div_text
         hasAddIndex = -1
         for index, item2 in enumerate(opening_data):
             if item2['date'] == date:
                 hasAddIndex = index
                 break
         if hasAddIndex == -1:
            opening_data.extend([{'date':date,'data':[item]}])
         else:
            opening_data[hasAddIndex]['data'].append(copy.deepcopy(item))
         # print(stock_backtest_data)
         # 将数据写入到 JSON 文件中
         with open(f'./full_data/{year}_opening_data.json', 'w') as file:
            json.dump(opening_data, file, ensure_ascii=False, indent=4) 

for item in stock_data:
    dates.append(item['date'])
    if len(opening_data) > 0 and opening_data[-1]['date'] == item['date'] and len(opening_data[-1]['data']) != len(item['data']):
       generateNextData(item['data'][len(opening_data[-1]['data']):],item['date'])
dates = dates[len(opening_data):]
stock_data = stock_data[len(opening_data):]

for idx, date in enumerate(dates):
    generateNextData(stock_data[idx]['data'],date)