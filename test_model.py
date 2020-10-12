import numpy as np
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import pandas as pd
# import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
# from pylab import rcParams
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

# %matplotlib inline
# %config InlineBackend.figure_format='retina'

# sns.set(style='whitegrid', palette='muted', font_scale=1.5)

# rcParams['figure.figsize'] = 16, 10

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
# tf.random.set_seed(RANDOM_SEED)

# QXBVAEK48AL618FI
ts = TimeSeries(key='QXBVAEK48AL618FI', output_format='pandas')
data = ""
try:
    data = ts.get_daily_adjusted(symbol='MSFT', outputsize='full')
except:
    print("error")
df = data[0]
print(len(df))

df = df.iloc[::-1]

train_size = int(len(df) * 0.8)
test_size = len(df) - train_size
train, test = df.iloc[0:train_size], df.iloc[train_size:len(df)]
# print(len(train), len(test))

train = train.drop(['4. close'], axis=1)
scaler = MinMaxScaler()
train = scaler.fit_transform(train)

X_train = []
y_train = []

for i in range(60, train.shape[0]):
    X_train.append(train[i-60:i])
    y_train.append(train[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)

# print(X_train.shape)

regressor = Sequential()

regressor.add(LSTM(units = 60, activation = 'relu', return_sequences = True, input_shape = (X_train.shape[1], 7)))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 60, activation = 'relu', return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 80, activation = 'relu', return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 120, activation = 'relu'))
regressor.add(Dropout(0.2))

regressor.add(Dense(units = 1))

# regressor.summary()

def train():
    regressor.compile(optimizer='adam', loss = 'mean_squared_error')
    regressor.fit(X_train, y_train, epochs=5, batch_size=32)
# train()
# testing data
train = df.iloc[0:train_size]
past_60_days = train.tail(60)

test_df = past_60_days.append(test, ignore_index=True)
test_df = test_df.drop(['4. close'], axis=1)
# print(test.tail(80))
inputs = scaler.transform(test_df)

X_test = []
y_test = []

for i in range(60, inputs.shape[0]):
    X_test.append(inputs[i-60:i])
    y_test.append(inputs[i, 0])

X_test, y_test = np.array(X_test), np.array(y_test)
# print(X_test.shape, y_test.shape)
y_pred = regressor.predict(X_test)
scale = 1/scaler.scale_[0]

y_pred = y_pred*scale
y_test = y_test*scale
y_pred = y_pred[-5:].tolist()
for i in range(5):
    y_pred[i] = str(y_pred[i][0])

print("\n".join(y_pred))
"""

plt.figure(figsize=(14,5))
plt.plot(y_test, color = 'red', label = 'Real Google Stock Price')
plt.plot(y_pred, color = 'blue', label = 'Predicted Google Stock Price')
plt.title('TSLA Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('TSLA Stock Price')
plt.legend()
plt.show()

"""
