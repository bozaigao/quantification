#龙头股开盘涨幅正太分布图
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
import os
import json

year = 2022
dip_increase_data = []

try:
    with open(f'{os.getcwd()}/backtest/{year}_dragon_backtest_data.json', 'r') as file:
        dragon_data = json.load(file)
except FileNotFoundError:
    dragon_data = []
for item in dragon_data:
    for item2 in item['data']:
        dip_increase_data.append(float(item2['opening_increase'].strip('%')))

# 使用 seaborn 绘制直方图和拟合的正态分布曲线
sns.histplot(dip_increase_data, kde=True, stat="density", color="skyblue")

# 生成正态分布拟合曲线的数据
mu, std = np.mean(dip_increase_data), np.std(dip_increase_data)
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

# 绘制正态分布曲线
plt.plot(x, p, 'k', linewidth=2)
title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
plt.title(title)

plt.show()
