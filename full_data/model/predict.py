import os
from stable_baselines3 import DQN

# 加载保存的模型
model = DQN.load(f'{os.getcwd()}/full_data/model/dqn_stock_model')

# 输入新状态，假设是股票的连板高度
new_stock_state = [150]  # 示例

# 预测动作
action, _ = model.predict(new_stock_state)

print("模型预测的动作是:", action)
