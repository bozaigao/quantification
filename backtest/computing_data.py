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

# 指定开始统计年份
year = 2024
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
# 指定年份的日期范围
dates = []
with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_dragon_opening_data.json', 'r') as file:
    dragon_opening_data = json.load(file)
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_dragon_backtest_data.json', 'r') as file:
        dragon_backtest_data = json.load(file)
except FileNotFoundError:
    dragon_backtest_data = []
for item in dragon_opening_data:
    dates.append(item['date'])
dates = dates[len(dragon_backtest_data):]
dragon_opening_data = dragon_opening_data[len(dragon_backtest_data):]
# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()

for idx, date in enumerate(dates):
    arr = []
    for item in dragon_opening_data[idx]['data']:
         # 获取上一个交易日
         date_object = datetime.strptime(date, '%Y-%m-%d').date()
         previous_date = calendar.valid_days(start_date='2000-01-01', end_date=date_object - timedelta(days=1))[-1]
         pre_increase = getIncrease(browserTab,str(previous_date.date()),item['name'])
         print(pre_increase)
         #获取当日收盘涨幅
         increase = getIncrease(browserTab,date,item['name'])
         #当日下探最低涨幅
         dip_increase = f'{round((float(increase[3]) - float(pre_increase[4]))/float(pre_increase[4])*100, 2)}%'
         #当日收盘涨幅
         close_increase = increase[0]
         #当日振幅
         shockValue = increase[5]
         # 判断是否为一字涨停的条件
         isLimitUpNoBuy = '一字涨停' in item['limit_type']
         #判断是否炸过板
         isBurst = item['limit_open_times'] != '0'
         # 获取下一个交易日
         date_object = datetime.strptime(date, '%Y-%m-%d').date()
         next_date = calendar.valid_days(start_date=date_object + timedelta(days=1), end_date='2100-01-01')[0]
         #获取次日竞价涨幅信息
         opening_increase = getOpeningIncrease(browserTab,str(next_date.date()),item['name'])
         #获取次日涨幅信息
         next_increase = getIncrease(browserTab,str(next_date.date()),item['name'])
         #次日收盘涨幅
         next_close_increase = next_increase[0]
         next_opening_increase = opening_increase[0]
         next_desc = opening_increase[1]
         nextIncrease = getIncrease(browserTab,str(next_date.date()),item['name'])
          # 判断次日是否涨停的条件
         if float(nextIncrease[0]) > 9.5 and nextIncrease[2] == nextIncrease[4]:
            next_isLimitUp = True
            print('涨停')
         else:
            next_isLimitUp = False
         #次日振幅
         next_shockValue = nextIncrease[5]
         # 判断次日是否为一字涨停的条件
         next_isLimitUpNoBuy = next_isLimitUp and next_shockValue == '0'
          # 判断次日是否跌停的条件
         if float(nextIncrease[0]) < -9.5 and nextIncrease[3] == nextIncrease[4]:
            next_isLimitDown = True
            print('跌停')
         else:
            next_isLimitDown = False
         # 判断次日是否为一字跌停的条件
         next_isLimitDownNoSale = next_isLimitDown and next_shockValue == '0'
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
         arr.append(item)
    dragon_backtest_data.extend([{'date':date,'data':arr}])
        # 将数据写入到 JSON 文件中
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_dragon_backtest_data.json', 'w') as file:
        json.dump(dragon_backtest_data, file, ensure_ascii=False, indent=4) 

   