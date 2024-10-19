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
model.learn(total_timesteps=400000)
model.save(f'./full_data/model/dqn_stock_model')

# 评估模型
obs, _ = env.reset()
for _ in range(env.total_steps):
    action, _states = model.predict(obs)
    obs, rewards, done, truncated, info = env.step(action)
    if done:
        break
    
def max_drawdown(assets):
    max_asset = np.maximum.accumulate(assets)
    drawdown = (max_asset - assets) / max_asset
    return np.max(drawdown)

# 初始化资产列表
total_assets = []

# 评估模型
obs, _ = env.reset()
for _ in range(env.total_steps):
    action, _states = model.predict(obs)
    obs, rewards, done, truncated, info = env.step(action)
    
    # 记录当前的总资产
    total_assets.append(env.balance)
    
    if done:
        break
# 计算并打印最大回撤
print(total_assets)
max_dd = max_drawdown(total_assets)
print(f'Max Drawdown: -{max_dd * 100:.2f}%')

#可视化累计收益曲线
plt.plot(total_assets)
plt.xlabel('Steps')
plt.ylabel('Total Assets')
plt.title('Cumulative Return Over Time')
plt.show()


# 初始化交易收益列表
# trades = []

# # 评估模型
# obs, _ = env.reset()
# for _ in range(env.total_steps):
#     action, _states = model.predict(obs)
#     obs, reward, done, truncated, info = env.step(action)
    
#     if action in [1, 2, 3, 4]:  # 记录买入或卖出操作
#         trades.append(reward)

#     if done:
#         break

# # 计算胜率
# win_rate = sum(1 for trade in trades if trade > 0) / len(trades)
# print(f'Win Rate: {win_rate * 100:.2f}%')





