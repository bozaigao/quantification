import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

# 读取数据
data = pd.read_csv('/mnt/data/data.txt')

# 特征工程
data['moving_avg'] = data['price'].rolling(window=5).mean()
data['return'] = data['price'].pct_change()

# 标签生成
data['target'] = np.where(data['return'] > 0, 1, 0)

# 数据拆分
train_data = data[data['date'] < '2023-01-01']
test_data = data[data['date'] >= '2023-01-01']

# 数据准备
X_train = train_data[['moving_avg', 'return']].values
y_train = train_data['target'].values
X_test = test_data[['moving_avg', 'return']].values
y_test = test_data['target'].values

# 模型构建
model = Sequential()
model.add(Dense(64, input_dim=2, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# 模型编译
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# 模型训练
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# 模型评估
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Loss: {loss}, Accuracy: {accuracy}')

# 生成交易信号
test_data['prediction'] = model.predict(X_test)
test_data['signal'] = np.where(test_data['prediction'] > 0.5, 1, 0)

# 回测
initial_capital = 100000
test_data['portfolio_value'] = initial_capital * (1 + test_data['return'].cumsum())

# 计算最终收益
final_value = test_data['portfolio_value'].iloc[-1]
print(f'Final Portfolio Value: {final_value}')
