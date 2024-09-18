import gymnasium as gym
from gymnasium import spaces
import numpy as np

class StockEnv(gym.Env):
    def __init__(self, stock_data):
        super(StockEnv, self).__init__()
        self.stock_data = stock_data  # 股票数据
        self.current_step = 0
        self.max_step = len(stock_data) - 1

        # 定义动作空间 (0: 空仓, 1: 买入 25% 仓位, 2: 买入 50% 仓位, 3: 买入 75% 仓位, 4: 买入 100% 仓位, 5: 持有, 6: 卖出)
        self.action_space = gym.spaces.Discrete(7)

        # 定义状态空间（假设状态是股票价格）
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(5,), dtype=np.float32)

        # 初始资金
        self.initial_balance = 100000
        self.balance = self.initial_balance
        self.current_stock_holding = 0

    def reset(self, seed=None, options=None):
        """重置环境，接受 seed 参数"""
        if seed is not None:
            np.random.seed(seed)

        self.current_step = 0
        self.balance = self.initial_balance
        self.current_stock_holding = 0

        return self._get_observation(), {}

    def step(self, action):
        """执行动作并返回状态、奖励、终止标志、截断标志和额外信息"""
        done = False
        truncated = False
        reward = 0

        # 获取当前股票价格
        current_price = self.stock_data[self.current_step]['price']

        # 根据动作执行交易逻辑
        if action == 0:
            # 空仓 - 什么都不做
            reward = 0
        elif action == 1:
            reward = self._take_action(0.25, current_price)
        elif action == 2:
            reward = self._take_action(0.5, current_price)
        elif action == 3:
            reward = self._take_action(0.75, current_price)
        elif action == 4:
            reward = self._take_action(1, current_price)
        elif action == 5:
            reward = 0  # 持有
        elif action == 6:
            reward = self._sell_action(1, current_price)

        # 移动到下一个时间步
        self.current_step += 1

        # 检查是否达到最后一步（自然终止条件）
        if self.current_step >= self.max_step:
            done = True

        # 如果账户余额用尽，可以认为达到终止状态
        if self.balance <= 0:
            done = True

        # 返回下一个状态，如果环境终止则返回全零状态
        next_state = self._get_observation() if not done else np.zeros(self.observation_space.shape)

        # 返回 (obs, reward, terminated, truncated, info)
        return next_state, reward, done, truncated, {}

    def _take_action(self, percentage, current_price):
        """买入操作，计算可以购买的股票数量并更新持仓和资金"""
        amount_to_invest = self.balance * percentage
        num_shares_bought = amount_to_invest / current_price

        # 更新持仓和余额
        self.current_stock_holding += num_shares_bought
        self.balance -= amount_to_invest

        # 假设买入收益为简单的价格变化
        reward = num_shares_bought * current_price / 100
        return reward

    def _sell_action(self, percentage, current_price):
        """卖出操作，计算卖出后的收益"""
        num_shares_to_sell = self.current_stock_holding * percentage
        amount_gained = num_shares_to_sell * current_price

        # 更新持仓和余额
        self.current_stock_holding -= num_shares_to_sell
        self.balance += amount_gained

        # 假设卖出收益为简单的价格变化
        reward = num_shares_to_sell * current_price / 100
        return reward

    def _get_observation(self):
        """获取当前的状态，返回状态数组"""
        current_data = self.stock_data[self.current_step]
        return np.array([
            current_data['price'],
            current_data['limit'],
            current_data['limit_ups'],
            current_data['limit_downs'],
            self.balance
        ])
