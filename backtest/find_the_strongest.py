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
find_date = datetime.strptime('2024-01-15', '%Y-%m-%d').date()
pre_date = '2024-01-12'
# pre_date = calendar.valid_days(start_date=find_date + timedelta(days=-1), end_date='2100-01-01')[0].date()
print(f'findDate:{str(find_date)},preDate:{str(pre_date)}')
for item in stocks_data:
    if item['date'] == str(find_date):
        for item2 in item['data']:
            pre_opening_increase = float(getOpeningIncrease(browserTab,str(pre_date),item2['name'])[0].strip('%'))
            current_opening_increase = float(getOpeningIncrease(browserTab,str(find_date),item2['name'])[0].strip('%'))
            if pre_opening_increase >= 9.5 and current_opening_increase >= 9.5 and abs(pre_opening_increase - current_opening_increase) <= 0.5:
                bothIsLimitPrice = True
            else:
                bothIsLimitPrice = False
            if current_opening_increase > pre_opening_increase or bothIsLimitPrice:
                strongest_pool.append({'date':str(find_date),'name':item2['name'],'desc':f'昨日竞价{pre_opening_increase}%,当日竞价{current_opening_increase}%','limit':item2['limit']})

for index, item in enumerate(strongest_pool):
    if item["limit"] > 2:
       print(Fore.RED + f'{index+1}.{item["name"]},{item["desc"]},{item["limit"]}板')
    else:
       print(Fore.GREEN + f'{index+1}.{item["name"]},{item["desc"]},{item["limit"]}板')


