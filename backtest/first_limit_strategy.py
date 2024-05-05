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
#初始建议仓位
suggest_shipping_space = 1
#资金记录
stockLog = []
#交易日期
dates = []
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stock_data = json.load(file)
except FileNotFoundError:
    stock_data = []


try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_first_limit_stock_log_data.json', 'r',) as file:
        first_limit_log_data = json.load(file)
except FileNotFoundError:
    first_limit_log_data = []

try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_new1_stocks_first_limit_backtest_data.json', 'r',) as file:
        first_limit_backtest_data = json.load(file)
except FileNotFoundError:
    first_limit_backtest_data = []

def formartNumber(earnings):
    return math.floor(earnings * 100) / 100

stockPool = []
#股票池
if len(first_limit_log_data) != 0 and 'stock' in first_limit_log_data[-1]:
   stockPool =  [first_limit_log_data[-1]['stock']]
if len(first_limit_log_data) != 0:
   suggest_shipping_space =  first_limit_log_data[-1]['suggest_shipping_space']

for item in first_limit_backtest_data:
    if len(first_limit_log_data)>0:
        latestMoney = first_limit_log_data[-1]['money']
    else:
        latestMoney = money
    #当前仓位
    if len(first_limit_log_data) > 0:
       current_shipping_space = first_limit_log_data[-1]['suggest_shipping_space']
    else:
       current_shipping_space = suggest_shipping_space
    #买入个股
    if len(stockPool) == 0 :
        targetPool = []
        hasStrongest = False
        for item2 in item['data']:
            if 'isBurst' in item2 and item2['first_limit_time']!='09:30:00' and item2['current_opening_increase'] < 8:
                targetPool.append(item2)
        targetPool = sorted(targetPool, key=lambda x: x['first_limit_time'])
        if len(targetPool) > 0:
            buyStock = targetPool[0]
            if not buyStock['isBurst']:
               first_limit_log_data.append({'date': item['date'], 'money':latestMoney,'suggest_shipping_space':current_shipping_space, 'earnings':'0%','desc':f'打板买入{buyStock["name"]},rank:{buyStock["rank"]}','stock':buyStock})
            else:
                earnings = float(buyStock['current_close_increase'])-10
                earnings = formartNumber(earnings)
                final_money = latestMoney + latestMoney * earnings/100
                first_limit_log_data.append({'date': item['date'], 'money':round(final_money),'suggest_shipping_space':current_shipping_space, 'earnings':f'{earnings}%','desc':f'打板买入{buyStock["name"]},结果炸板了盈利{earnings}%,rank:{buyStock["rank"]}','stock':buyStock})
            stockPool.append(buyStock)
        else:
            first_limit_log_data.append({'date': item['date'], 'money':round(latestMoney),'suggest_shipping_space':current_shipping_space, 'earnings':f'{0}%','desc':f'空仓'})
            stockPool = []
    #卖出个股
    else:
         buyStock = stockPool[0]
         next_opening_increase = float(buyStock['next_close_increase'])
         final_money = latestMoney + latestMoney * current_shipping_space * next_opening_increase/100
         if next_opening_increase < 0:
            next_shipping_space = 1
        #    next_shipping_space = current_shipping_space * 0.5
         #如果出现盈利，马上又推全仓
         else:
            next_shipping_space = 1
         first_limit_log_data.append({'date':item['date'], 'money':round(final_money),'suggest_shipping_space':next_shipping_space, 'earnings':f'{next_opening_increase}%','desc':f'竞价卖出{buyStock["name"]},当日盈利{next_opening_increase}%'})
         stockPool = []
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_first_limit_stock_log_data.json', 'w') as file:
        json.dump(first_limit_log_data, file,ensure_ascii=False,  indent=4) 