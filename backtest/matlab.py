import matplotlib.pyplot as plt
from datetime import datetime
import os
import json

year = 2024
try:
    with open(f'{os.getcwd()}/backtest/{year}_stock_log_data.json', 'r') as file:
        dragon_log_data = json.load(file)
except FileNotFoundError:
    dragon_log_data = []
print(len(dragon_log_data))
# index = 0
# for _index,item in enumerate(dragon_log_data):
#     if item['date'] == '2023-04-28':
#         index = _index
# dragon_log_data = dragon_log_data[:index]

# 提取日期和资金数据
dates = [datetime.strptime(entry["date"], "%Y-%m-%d") for entry in dragon_log_data]
money_values = [entry["money"] for entry in dragon_log_data]

# 绘制资金增长曲线
plt.plot(dates, money_values, '-o')
plt.xlabel('Date')
plt.ylabel('Money')
plt.title('Capital Growth Curve')
plt.grid(True)
plt.show()
