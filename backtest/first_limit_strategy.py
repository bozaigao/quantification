import os
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
from  utils.judgeBurst import judgeBurst
import pychrome
import math
from colorama import Fore, Back, Style

# 指定回测年份
year = 2024
#初始资金
money = 100000
#资金记录
stockLog = []
#交易日期
dates = []
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_first_limit_stock_log_data.json', 'r',) as file:
        first_limit_log_data = json.load(file)
except FileNotFoundError:
    first_limit_log_data = []

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_new_stocks_first_limit_backtest_data.json', 'r',) as file:
        first_limit_backtest_data = json.load(file)
except FileNotFoundError:
    first_limit_backtest_data = []

def formartNumber(earnings):
    return math.floor(earnings * 100) / 100

stockPool = []
#股票池
if len(first_limit_log_data) != 0 and 'stock' in first_limit_log_data[-1]:
   stockPool =  [first_limit_log_data[-1]['stock']]

for item in first_limit_backtest_data:
    if len(first_limit_log_data)>0:
        latestMoney = first_limit_log_data[-1]['money']
    else:
        latestMoney = money
    #买入个股
    if len(stockPool) == 0 :
        targetPool = []
        hasStrongest = False
        for item2 in item['data']:
            if 'isBurst' in item2 and item2['first_limit_time']=='09:30:00':
                hasStrongest = True
            if 'isBurst' in item2 and item2['first_limit_time']!='09:30:00' and item2['current_opening_increase'] < 8 and float(item2['pre_jinliang']) > 0 and float(item2['huanshou']) > float(item2['pre_huanshou']):
                targetPool.append(item2)
        targetPool = sorted(targetPool, key=lambda x: x['first_limit_time'])
        if len(targetPool) > 0:
            buyStock = targetPool[0]
            if not buyStock['isBurst']:
               first_limit_log_data.append({'date': item['date'], 'money':latestMoney, 'earnings':'0%','desc':f'打板买入{buyStock["name"]},rank:{buyStock["rank"]}','stock':buyStock})
            else:
                earnings = float(buyStock['current_close_increase'])-10
                earnings = formartNumber(earnings)
                final_money = latestMoney + latestMoney * earnings/100
                first_limit_log_data.append({'date': item['date'], 'money':round(final_money), 'earnings':f'{earnings}%','desc':f'打板买入{buyStock["name"]},结果炸板了盈利{earnings}%,rank:{buyStock["rank"]}','stock':buyStock})
            stockPool.append(buyStock)
        else:
            first_limit_log_data.append({'date': item['date'], 'money':round(latestMoney), 'earnings':f'{0}%','desc':f'空仓'})
            stockPool = []
    #卖出个股
    else:
         buyStock = stockPool[0]
         next_opening_increase = formartNumber(float(buyStock['next_opening_increase'].strip('%')))
         final_money = latestMoney + latestMoney * next_opening_increase/100
         first_limit_log_data.append({'date':item['date'], 'money':round(final_money), 'earnings':f'{next_opening_increase}%','desc':f'竞价卖出{buyStock["name"]},当日盈利{next_opening_increase}%'})
         stockPool = []
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_first_limit_stock_log_data.json', 'w') as file:
        json.dump(first_limit_log_data, file,ensure_ascii=False,  indent=4) 