import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
import pychrome
import math

year = 2024
try:
    with open(f'{os.getcwd()}/backtest/{year}_first_limit_stock_log_data.json', 'r') as file:
        stock_log_data = json.load(file)
except FileNotFoundError:
    stock_log_data = []
try:
    with open(f'{os.getcwd()}/backtest/{year}_new1_stocks_first_limit_backtest_data.json', 'r') as file:
        stock_data = json.load(file)
except FileNotFoundError:
    stock_data = []
success = 0
fail = 0
count = 0
kongcang = 0
for item in stock_log_data:
    if float(item['earnings'].strip('%')) < -5:
        print(item['date'], item['desc'])
#     if '空仓' not in item['desc']:
#         count += 1
#         if 'stock' in item and item['earnings'] == '0%':
#             # print(f'{item["date"]},{item["desc"]}')
#             success += 1
#         elif 'stock' in item and item['earnings'] != '0%':
#             print(f'{item["date"]},{item["desc"]}')
#             fail += 1
#     else:
#         kongcang += 1
# print(success/(fail+success),success,fail,kongcang,count)

# for item in stock_data:
#     for item2 in item['data']:
#         # if float(item2['pre_jinliang']) < 0 and not item2['isBurst']:
#         #     print(item['date'],item2['name'])
#         if item2['pre_final_limit_time'] > '11:30:00' and float(item2['next_opening_increase'].strip('%')) > 5:
#             count += 1
#             print(item['date'],item2['name'])
       
# print(count)