#找出指定日期资金流入最强个股
import os
import re
import json
from datetime import datetime, timedelta
from pandas_market_calendars import get_calendar
from utils.opening_increase import getOpeningIncrease
from  utils.judgeBurst import judgeBurst
import pychrome
import math
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt

# 指定回测年份
year = 2024
try:
    with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_first_limit_backtest_data.json', 'r',) as file:
        stocks_backtest_data = json.load(file)
except FileNotFoundError:
    stocks_backtest_data = []
jinliangData = []
for item in stocks_backtest_data:
    sorted_data = sorted(item['data'], key=lambda x: float(x["jinliang"]), reverse=True)
    sorted_data = sorted_data[:3]
    jinliangData.append({'date':item['date'],'data':sorted_data})
with open(f'{os.getcwd().replace("/backtest", "")}/backtest/{year}_stocks_first_limit_jinliang.json', 'w') as file:
        json.dump(jinliangData, file,ensure_ascii=False,  indent=4) 
        
         