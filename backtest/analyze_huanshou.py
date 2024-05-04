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
success = 0
fail = 0
count = 0
for item in stock_log_data:
    if '空仓' not in item['desc']:
        count += 1
        if 'stock' in item and item['earnings'] == '0%':
            success += 1
        elif 'stock' in item and item['earnings'] != '0%':
            fail += 1
      
print(success/(fail+success),count)