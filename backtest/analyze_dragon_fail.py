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
        dragon_backtest_data = json.load(file)
except FileNotFoundError:
    dragon_backtest_data = []
count = 0
for item in dragon_backtest_data:
    for item2 in item['data']:
        if item2['next_isBurst']:
           count += 1
           print(f'{item["date"]},{item2["name"]}')
print(count)
