import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
import pychrome
import math

year = 2024
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
try:
    with open(f'{os.getcwd()}/backtest/{year}_dragon_backtest_data.json', 'r') as file:
        dragon_data = json.load(file)
except FileNotFoundError:
    dragon_data = []

def yestodayIsYiZi(date, code):
    # 获取上一个交易日
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    previous_date = calendar.valid_days(start_date='2000-01-01', end_date=date_object - timedelta(days=1))[-1]
    for item3 in dragon_data:
        if item3['date'] == str(previous_date.date()):
           for item4 in item3['data']:
               if '一字' in item4["limit_type"] and item4["code"] == code:
                  return True
    return False

for item in dragon_data:
    for item2 in item['data']:
        # if not '一字' in item2["limit_type"] and item2["next_isLimitUp"] and yestodayIsYiZi(item['date'],item2['code']) and len(item['data']) == 1:
        #    print(f'{item["date"]} {item2["name"]}')
        # if '一字' in item2["limit_type"] and item2["next_isBurst"] and len(item['data']) == 1:
        #    print(f'{item["date"]} {item2["name"]}')
         if '一字' in item2["limit_type"] and len(item['data']) == 1:
           print(f'{item["date"]} {item2["name"]}')
 
