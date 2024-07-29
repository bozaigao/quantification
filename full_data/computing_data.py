#生成可以进行回溯计算的数据
#数据结构包含股票名字、股票代码、最高板数、开盘涨幅、收盘涨幅、是否涨停、是否跌停、是否一字涨停、是否一字跌停、当日是否炸板、
#次日开盘涨幅、次日收盘涨幅、次日是否涨停、次日是否跌停、次日是否一字涨停、次日是否一字跌停、次日是否炸板
from bs4 import BeautifulSoup
import pychrome
import json
import re
from pandas_market_calendars import get_calendar
from datetime import datetime, timedelta
import os
from  utils.increase import getIncrease
from  utils.judgeBurst import judgeBurst
from  utils.opening_increase import getOpeningIncrease
import copy
print(os.getcwd())
# 指定开始统计年份
year = 2021
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
#是否输出策略分析
forecast = False
if '/backtest' in os.getcwd():
   forecast = True
# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()
# 指定年份的日期范围
dates = []
with open(f'./full_data/{year}_opening_data.json', 'r') as file:
    stock_opening_data = json.load(file)
try:
    with open(f'./full_data/{year}_stock_backtest_data.json', 'r') as file:
        stock_backtest_data = json.load(file)
except FileNotFoundError:
    stock_backtest_data = []
if forecast:
    stock_backtest_data = stock_backtest_data[:-1]

def generateNextData(data,date):
    for item in data:
         # 获取上一个交易日
         date_object = datetime.strptime(date, '%Y-%m-%d').date()
         previous_date = calendar.valid_days(start_date='2000-01-01', end_date=date_object - timedelta(days=1))[-1]
         pre_increase = getIncrease(browserTab,str(previous_date.date()),item['code'])
         print(f'😁${pre_increase}')
         #获取当日收盘涨幅
         increase = getIncrease(browserTab,date,item['code'])
         print(f'😁涨幅${increase}')
         #当日下探最低涨幅
         dip_increase = f'{round((float(increase[3]) - float(pre_increase[4]))/float(pre_increase[4])*100, 2)}%'
         #当日收盘涨幅
         close_increase = increase[0]
         #当日振幅
         shockValue = increase[5]
         #判断是否炸过板
         isBurst = item['limit_open_times'] != '0'
         # 获取下一个交易日
         date_object = datetime.strptime(date, '%Y-%m-%d').date()
         next_date = calendar.valid_days(start_date=date_object + timedelta(days=1), end_date='2100-01-01')[0]
         #获取次日竞价涨幅信息
         opening_increase = getOpeningIncrease(browserTab,str(next_date.date()),item['code'])
         #获取次日涨幅信息
         next_increase = getIncrease(browserTab,str(next_date.date()),item['code'])
         #次日收盘涨幅
         next_close_increase = next_increase[0]
         next_opening_increase = opening_increase[0]
         next_desc = opening_increase[1]
         nextIncrease = getIncrease(browserTab,str(next_date.date()),item['code'])
          # 判断次日是否涨停的条件
         if float(nextIncrease[0]) > 9.5 and nextIncrease[2] == nextIncrease[4]:
            next_isLimitUp = True
            print('涨停')
         else:
            next_isLimitUp = False
         #次日振幅
         next_shockValue = nextIncrease[5]
         print(f'😁${nextIncrease}')
         # 判断次日是否为一字涨停的条件
         next_isLimitUpNoBuy = next_isLimitUp and float(next_shockValue) == 0
          # 判断次日是否跌停的条件
         if float(nextIncrease[0]) < -9.5 and nextIncrease[3] == nextIncrease[4]:
            next_isLimitDown = True
            print('跌停')
         else:
            next_isLimitDown = False
         # 判断次日是否为一字跌停的条件
         next_isLimitDownNoSale = next_isLimitDown and float(next_shockValue) == 0
         #判断次日是否炸过板
         burstData = judgeBurst(browserTab,str(next_date.date()),item['code'])
         item['isBurst'] = isBurst
         item['dip_increase'] = dip_increase
         item['shockValue'] = shockValue
         item['next_isLimitUp'] = next_isLimitUp
         item['next_isLimitUpNoBuy'] = next_isLimitUpNoBuy
         item['next_isLimitDown'] = next_isLimitDown
         item['next_isLimitDownNoSale'] = next_isLimitDownNoSale
         item['next_isBurst'] = burstData[0]
         item['next_burst_time'] = burstData[1]
         item['next_shockValue'] = next_shockValue
         item['next_opening_increase'] = next_opening_increase
         item['next_desc'] = next_desc
         item['close_increase'] = close_increase
         item['next_close_increase'] = next_close_increase
         hasAddIndex = -1
         for index, item2 in enumerate(stock_backtest_data):
             if item2['date'] == date:
                 hasAddIndex = index
                 break
         if hasAddIndex == -1:
            stock_backtest_data.extend([{'date':date,'data':[item]}])
         else:
            stock_backtest_data[hasAddIndex]['data'].append(copy.deepcopy(item))
         # print(stock_backtest_data)
         # 将数据写入到 JSON 文件中
         with open(f'./full_data/{year}_stock_backtest_data.json', 'w') as file:
            json.dump(stock_backtest_data, file, ensure_ascii=False, indent=4) 

for item in stock_opening_data:
    dates.append(item['date'])
    if len(stock_backtest_data) > 0 and stock_backtest_data[-1]['date'] == item['date'] and len(stock_backtest_data[-1]['data']) != len(item['data']):
       generateNextData(item['data'][len(stock_backtest_data[-1]['data']):],item['date'])

dates = dates[len(stock_backtest_data):]
stock_opening_data = stock_opening_data[len(stock_backtest_data):]

for idx, date in enumerate(dates):
    generateNextData(stock_opening_data[idx]['data'],date)

   