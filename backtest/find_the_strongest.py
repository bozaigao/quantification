#找出指定日期资金流入最强个股
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
#交易日期
dates = []
# 获取中国交易日历
calendar = get_calendar('XSHG')  # 'XSHG' 表示上海证券交易所的交易日历
# 创建一个Browser实例
browser = pychrome.Browser(url="http://127.0.0.1:9222")
# 新建一个标签页
browserTab = browser.new_tab()
# 打开链接
browserTab.start()
browserTab.Network.enable()
strongest_pool = []
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'r',) as file:
        stocks_data = json.load(file)
except FileNotFoundError:
    stocks_data = []
# find_date = datetime.now().date()
find_date = datetime.strptime('2024-04-22', '%Y-%m-%d').date()
pre_date = '2024-04-19'
# pre_date = calendar.valid_days(start_date=find_date + timedelta(days=-1), end_date='2100-01-01')[0].date()
print(f'今日:{str(find_date)},昨日:{str(pre_date)}')
for index1, item in enumerate(stocks_data):
    if item['date'] == str(pre_date):
        for index2, item2 in enumerate(item['data']):
            if item2['limit'] > 1:
                if "current_opening_increase" in stocks_data[index1]["data"][index2]:
                    pre_opening_increase = float(stocks_data[index1]["data"][index2]["current_opening_increase"].strip('%'))
                else:
                    pre_opening_increase = float(getOpeningIncrease(browserTab,str(pre_date),item2['code'])[0].strip('%'))
                    stocks_data[index1]["data"][index2]["current_opening_increase"] = f'{pre_opening_increase}%'
                if "next_opening_increase" in stocks_data[index1]["data"][index2]:
                    current_opening_increase = float(stocks_data[index1]["data"][index2]["next_opening_increase"].strip('%'))
                else:
                    current_opening_increase = float(getOpeningIncrease(browserTab,str(find_date),item2['code'])[0].strip('%'))
                    stocks_data[index1]["data"][index2]["next_opening_increase"] = f'{current_opening_increase}%'
                if pre_opening_increase >= 9.5 and current_opening_increase >= 9.5 and abs(pre_opening_increase - current_opening_increase) <= 0.5:
                    bothIsLimitPrice = True
                else:
                    bothIsLimitPrice = False
                if current_opening_increase > pre_opening_increase or bothIsLimitPrice:
                   strongest_pool.append({'date':str(find_date),'name':item2['name'],'pre_opening_increase':pre_opening_increase,'current_opening_increase':current_opening_increase,'limit':item2['limit']})

strongest_pool = sorted(strongest_pool, key=lambda x: (-x['limit'], -x['current_opening_increase']))
for index, item in enumerate(strongest_pool):
    if item["limit"] > 2:
       print(Fore.RED + f'{index+1}.{item["name"]},昨日竞价{item["pre_opening_increase"]}%,当日竞价{item["current_opening_increase"]}%,{item["limit"]}板, 振幅{round(abs(item["current_opening_increase"] - item["pre_opening_increase"]),2)}%')
    else:
       print(Fore.GREEN + f'{index+1}.{item["name"]},昨日竞价{item["pre_opening_increase"]}%,当日竞价{item["current_opening_increase"]}%,{item["limit"]}板, 振幅{round(abs(item["current_opening_increase"] - item["pre_opening_increase"]),2)}%')

with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_data.json', 'w') as file:
        json.dump(stocks_data, file,ensure_ascii=False,  indent=4) 

