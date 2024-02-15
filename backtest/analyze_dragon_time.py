#龙头股涨停时间分布
import os
import json
from datetime import datetime

year = 2024

def isEarly(first_limit_time, compared_time):
    # 将字符串转换为时间对象
    first_limit_datetime = datetime.strptime(first_limit_time, '%H:%M:%S')
    compared_datetime = datetime.strptime(compared_time, '%H:%M:%S')
    # 比较时间
    return first_limit_datetime <= compared_datetime

try:
    with open(f'{os.getcwd()}/backtest/{year}_dragon_backtest_data.json', 'r') as file:
        dragon_data = json.load(file)
except FileNotFoundError:
    dragon_data = []

count1 = 0
count2 = 0
count3 = 0
count4 = 0
count5 = 0
count6 = 0
for item in dragon_data:
    for item2 in item['data']:
        if isEarly(item2['first_limit_time'], '09:30:00'):
           count1 += 1
        elif isEarly(item2['first_limit_time'], '09:35:00'):
           count2 += 1
        elif isEarly(item2['first_limit_time'], '09:45:00'):
           count3 += 1
        elif isEarly(item2['first_limit_time'], '10:00:00'):
           count4 += 1
        elif isEarly(item2['first_limit_time'], '11:30:00'):
           count5 += 1
        else:
           count6 += 1
         #   print(item['date'],item2['name'])
print(f'09:30:00之前涨停的龙头股有{count1}个')
print(f'09:35:00之前涨停的龙头股有{count2}个')
print(f'09:45:00之前涨停的龙头股有{count3}个')
print(f'10:00:00之前涨停的龙头股有{count4}个')
print(f'11:30:00之前涨停的龙头股有{count5}个')
print(f'剩下涨停的龙头股有{count6}个')