#计算当日最高标开盘涨幅，如果有多个最高表则平均计算
from bs4 import BeautifulSoup
import pychrome
import json
import re
from pandas_market_calendars import get_calendar

global_wait_seconds = 3
# 指定开始统计年份
year = 2024
with open(f'./full_data/{year}_stocks_data.json', 'r') as file:
        stock_data = json.load(file)
# 指定年份的日期范围
dates = []# 这里替换为你的交易日日期列表
for item in stock_data:
    dates.append(item['date'])
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
stock_data = stock_data[len(opening_data):]
dates = dates[len(opening_data):]
for idx, workday in enumerate(dates):
    arr = []
    for item in stock_data[idx]['data']:
        browserTab.Page.navigate(url=f"https://www.iwencai.com/unifiedwap/result?w={workday} '{item['code']}'竞价涨幅&querytype=stock")
        browserTab.wait(global_wait_seconds)
        result = browserTab.Runtime.evaluate(expression="document.documentElement.outerHTML")
        soup = BeautifulSoup(result['result']['value'], 'html.parser')
        div_text = soup.find('div', class_='jgy_txt_isLayout').get_text(strip=True)
        paragraphs = soup.find_all('p', recursive=False)
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
        arr.append(item)
    opening_data.extend([{'date':workday,'data':arr}])
    with open(f'./full_data/{year}_opening_data.json', 'w') as file:
         json.dump(opening_data, file,ensure_ascii=False,  indent=4) 

   