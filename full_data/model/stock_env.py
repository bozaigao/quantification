import gymnasium as gym
from gymnasium import spaces
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

def _time_to_seconds(time_str):
    t = datetime.strptime(time_str, '%H:%M:%S')
    return t.hour * 3600 + t.minute * 60 + t.second

class StockEnv(gym.Env):
    def __init__(self, stock_data):
        super(StockEnv, self).__init__()
        self.limit_reason_encoder = LabelEncoder()
        self.limit_type_encoder = LabelEncoder()
        self.stock_data = stock_data  # 股票数据
        self.limit_reason_encoder.fit(self.stock_data['limit_reason'])
        self.limit_type_encoder.fit(self.stock_data['limit_type'])
        self.total_steps = len(self.stock_data)
        self.current_step = 0
        self.max_step = len(stock_data) - 1

        # 定义动作空间 (0: 空仓, 1: 涨停买入 25% 仓位, 2: 涨停买入 50% 仓位, 3: 涨停买入 75% 仓位, 4: 涨停买入 100% 仓位, 5: 持有, 6: 竞价卖出， 7: 涨停卖出)
        self.action_space = gym.spaces.Discrete(8)

        # 初始资金
        self.initial_balance = 100000
        self.balance = self.initial_balance
        # 当前仓位
        self.current_shipping_space = 0
          # 定义状态空间
        obs_shape = self._get_observation().shape
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=obs_shape, dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        """重置环境，接受 seed 参数"""
        if seed is not None:
            np.random.seed(seed)

        self.current_step = 0
        self.balance = self.initial_balance
        self.current_shipping_space = 0

        return self._get_observation(), {}

    def step(self, action):
        """执行动作并返回状态、奖励、终止标志、截断标志和额外信息"""
        done = False
        truncated = False
        reward = 0
        
        obs, reward, done, truncated, _ = self._take_action(action)
        
        if self.current_step >= self.total_steps:
            done = True
        
        return obs, reward, done, truncated, {}

    def _take_action(self, action):
        if self.current_step >= self.total_steps:
            return self._get_observation(), 0, True, False, {}
        stock = self.stock_data.iloc[self.current_step]
        reward = 0

        if action == 0:
            # 空仓 - 什么都不做
            reward = 0
        elif action in [1, 2, 3, 4, 5]:  # Buy actions (25%, 50%, 75%, 100%)
            if self.current_shipping_space == 0:
                self.current_shipping_space = action * 0.25  # Map actions to purchase % (25%, 50%, 75%, 100%)
                # 当日收盘涨幅（如果未维持涨停，计算负收益）
                close_increase = stock['close_increase']
                if close_increase < 10:  # 如果收盘没有维持涨停板（10%）
                    # 当日收益为负：当日涨幅 - 涨停涨幅
                    today_reward = close_increase - 0.10
                else:
                    # 当日收盘维持涨停，当日收益为0
                    today_reward = 0
                # 次日开盘涨幅
                next_day_reward = stock['next_opening_increase']

                # 总奖励为当日收益 + 次日开盘涨幅
                reward = (today_reward + next_day_reward) * self.current_shipping_space
                reward = float("{:.3f}".format(reward))  # 精确到小数点后三位
                if today_reward < 0:
                    self.balance += self.balance * today_reward * self.current_shipping_space
                    self.balance = int(self.balance)
            elif action == 5 and self.current_shipping_space != 0:
                # 当日收盘涨幅（如果未维持涨停，计算负收益）
                close_increase = stock['close_increase']
                if close_increase < 10:  # 如果收盘没有维持涨停板（10%）
                    # 当日收益为负：当日涨幅 - 涨停涨幅
                    today_reward = close_increase - 0.10
                else:
                    # 当日收盘维持涨停，当日收益为0
                    today_reward = 0
                # 次日开盘涨幅
                next_day_reward = stock['next_opening_increase']

                # 总奖励为当日收益 + 次日开盘涨幅
                reward = (today_reward + next_day_reward) * self.current_shipping_space
                reward = float("{:.3f}".format(reward))  # 精确到小数点后三位
                if today_reward < 0:
                    self.balance += self.balance * today_reward * self.current_shipping_space
                    self.balance = int(self.balance)
            else:
                reward = 0  # Can't buy if already holding stock
        elif action == 6:  # Sell in auction
            if self.current_shipping_space > 0:
                reward = stock['opening_increase'] * self.current_shipping_space
                reward = float("{:.3f}".format(reward))
                self.balance += self.balance * reward
                self.balance = int(self.balance)
                self.current_shipping_space = 0
                reward = 0
            else:
                reward = 0  # Can't sell if not holding stock
        elif action == 7:  # Sell at limit
            if self.current_shipping_space > 0:
                reward =  self.current_shipping_space * 0.10  # 10% reward for selling at upper limit
                reward = float("{:.3f}".format(reward))
                self.balance += self.balance * reward
                self.balance = int(self.balance)
                self.current_shipping_space = 0
                reward = 0
            else:
                reward = 0  # Can't sell if not holding stock

        self.current_step += 1
        done = self.current_step >= self.total_steps
        truncated = False
        obs = self._get_observation()
        # print('😁_take_action->>reward', self.balance)

        return obs, reward, done, truncated, {}

    def _get_observation(self):
        """返回当前状态，包含资金、持仓和股票特征等"""
        # 如果 current_step 超出数据范围，返回一个默认值
        if self.current_step >= len(self.stock_data):
            return np.zeros(13, dtype=np.float32)  # 返回默认的全0观测值

        stock = self.stock_data.iloc[self.current_step]
        obs = np.array([
            self.balance,
            self.current_shipping_space,
            stock['limit'],
            stock['limit_ups'],
            stock['limit_downs'],
            stock['limit_cheng_ratio'],
            stock['limit_liu_ratio'],
            stock['limit_open_times'],
            stock['market_value'],
            stock['shockValue'],
            stock['next_shockValue'],
            stock['opening_increase'],
            stock['next_opening_increase']
        ], dtype=np.float32)  # 确保返回类型为 float32
        
        return obs

