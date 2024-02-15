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
count1 = 0
count2 = 0
for item in dragon_data:
    for item2 in item['data']:
        if not item2["next_isLimitUp"]:
           print(f'{item["date"]}_{item2["name"]}')
 
