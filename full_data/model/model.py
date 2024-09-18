import os
from stable_baselines3 import DQN
from stock_env import StockEnv
import json
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# try:
#     with open(f'./full_data/model/2024_stock_backtest_data.json', 'r',) as file:
#         data = json.load(file)
# except FileNotFoundError:
#     data = []
data = pd.read_json(f'./full_data/model/2024_stock_backtest_data.json')

# 展开日期和数据
data = data.explode('data').reset_index(drop=True)

# 将嵌套的'data'字典展开
data = pd.concat([data.drop(['data'], axis=1), data['data'].apply(pd.Series)], axis=1)

# 处理数据类型，例如将百分比字符串转换为浮点数
data['current_opening_increase'] = data['current_opening_increase'].str.rstrip('%').astype('float') / 100.0
data['next_opening_increase'] = data['next_opening_increase'].str.rstrip('%').astype('float') / 100.0
data['opening_increase'] = data['opening_increase'].str.rstrip('%').astype('float') / 100.0
data['dip_increase'] = data['dip_increase'].str.rstrip('%').astype('float') / 100.0
data['close_increase'] = data['close_increase'].astype('float') / 100.0
data['next_close_increase'] = data['next_close_increase'].astype('float') / 100.0
# 对其他需要的列进行类似的处理

# 填充缺失值或删除缺失值
data = data.fillna(0)

env = StockEnv(data)
check_env(env)
model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100000)
model.save("dqn_stock_model")
obs = env.reset()
for _ in range(len(env.data)):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    if done:
        break

total_assets = []
obs = env.reset()
for _ in range(len(env.data)):
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)
    total_assets.append(env.total_asset)
    if done:
        break

plt.plot(total_assets)
plt.xlabel('时间步')
plt.ylabel('总资产')
plt.title('资产变化曲线')
plt.show()




