import os
from stable_baselines3 import DQN
from stock_env import StockEnv
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_json(f'./full_data/model/2024_stock_backtest_data.json')

# 展开日期和数据
data = data.explode('data').reset_index(drop=True)

# 将嵌套的'data'字典展开
data = pd.concat([data.drop(['data'], axis=1), data['data'].apply(pd.Series)], axis=1)

# 处理百分比字符串，将它们转换为浮点数
percentage_columns = [
    'current_opening_increase', 
    'next_opening_increase', 
    'opening_increase', 
    'dip_increase', 
    'close_increase', 
    'next_close_increase'
]

for col in percentage_columns:
    data[col] = data[col].str.rstrip('%').astype('float') / 100.0

# 处理数值列，将字符串类型的数值转换为浮点数
numeric_columns = [
    'price', 
    'limit', 
    'limit_ups', 
    'limit_downs', 
    'limit_cheng_ratio', 
    'limit_liu_ratio', 
    'limit_open_times', 
    'market_value', 
    'shockValue', 
    'next_shockValue'
]

for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# 填充缺失值或删除缺失值
data = data.fillna(0)

env = StockEnv(data)
check_env(env)
model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)
model.save(f'./full_data/model/dqn_stock_model')
# 评估模型
obs, _ = env.reset()
for _ in range(env.total_steps):
    action, _states = model.predict(obs)
    obs, rewards, done, truncated, info = env.step(action)
    if done:
        break

# 可视化结果
total_assets = []
obs, _ = env.reset()
for _ in range(env.total_steps):
    action, _states = model.predict(obs)
    obs, reward, done, truncated, info = env.step(action)
    total_assets.append(env.total_asset)
    if done:
        break

import matplotlib.pyplot as plt

plt.plot(total_assets)
plt.xlabel('时间步')
plt.ylabel('总资产')
plt.title('资产变化曲线')
plt.show()





