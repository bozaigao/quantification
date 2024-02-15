import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
import pychrome
import math

year = 2024
try:
    with open(f'{os.getcwd()}/backtest/{year}_dragon_backtest_data.json', 'r') as file:
        dragon_data = json.load(file)
except FileNotFoundError:
    dragon_data = []

for item in dragon_data:
    for item2 in item['data']:
        if '一字涨停' not in item2['limit_type'] and float(item2['next_opening_increase'].strip('%')) > 5:
            print(f'{item["date"]},{item2["name"]}')
