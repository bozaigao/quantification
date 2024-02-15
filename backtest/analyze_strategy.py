import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
import pychrome
import math

year = 2024
try:
    with open(f'{os.getcwd()}/backtest/{year}_stock_log_data.json', 'r') as file:
        dragon_log_data = json.load(file)
except FileNotFoundError:
    dragon_log_data = []

kongcang = 0
peak = dragon_log_data[0]['money']
max_drawdown = 0
for item in dragon_log_data:
    current_money = item['money']
    increase = float(item["earnings"].strip('%'))
    if current_money > peak:
        peak = current_money
    else:
        drawdown = (peak - current_money) / peak
        max_drawdown = max(max_drawdown, drawdown)
    if '空仓' in item['desc']:
        kongcang += 1
    if increase < 0:
       print(f'{item["date"]} {item["desc"]}')
print(f'{len(dragon_log_data)}个交易日,空仓了{kongcang}天,资金最大回撤{round(max_drawdown * 100)}%')
