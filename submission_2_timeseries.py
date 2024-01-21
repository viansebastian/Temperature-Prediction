# -*- coding: utf-8 -*-
"""Submission 2: TimeSeries.ipynb

Automatically generated by Colaboratory.

# Submission 2: Time Series
Vian Sebastian Bromokusumo

> username: vianvian


> email: viansebastianbromokusumo@mail.ugm.ac.id
"""

# Criteria:
# 1. Min. 10000 samples                         <----->
# 2. LSTM architecture                          <----->
# 3. Validation set = 20%                       <----->
# 4. Sequential model                           <----->
# 5. Apply Learning Rate in the Optimizer       <----->
# 6. MAE < 10% data scale                       <----->
# 7. Apply callbacks                            <----->
# 8. Plot loss and accuracy for train and val   <----->

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf

df = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/Dicoding Intermediate/weather_features.csv')
df.head()

df.tail()

df.isnull().sum()

df.shape

grouped_data = df.groupby('city_name')
city_data_count = grouped_data.size()

print(city_data_count)

sliced_data = df[df['city_name'] == 'Seville']
sliced_data = sliced_data[['dt_iso','temp']]

sliced_data

sliced_data.isnull().sum()

plt.subplots(figsize=(15,5))
sns.lineplot(data = sliced_data['temp'])
plt.title('temperature')
plt.xlabel('Date')
plt.ylabel('Temp')

sliced_data['dt_iso'] = pd.to_datetime(sliced_data['dt_iso'])

sliced_data

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

sliced_data['dt_iso'] = pd.to_datetime(sliced_data['dt_iso'], utc = True)

temp_values = sliced_data['temp'].values.reshape(-1, 1)

scaler = MinMaxScaler()

normalized_temp = scaler.fit_transform(temp_values)

sliced_data['normalized_temp'] = normalized_temp

sliced_data

x = sliced_data['dt_iso']
y = sliced_data['normalized_temp']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, shuffle = False)

print(len(x_train))
print(len(x_test))

print(len(y_train))
print(len(y_test))

y_test

x_train

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    # series = np.array(series)
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

ws = 60

train_set = windowed_dataset(y_train, window_size = ws, batch_size = 100, shuffle_buffer = 100)
test_set = windowed_dataset(y_test, window_size = ws, batch_size = 10, shuffle_buffer = 1)

model = tf.keras.models.Sequential([
  tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences = True)),
  tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
  tf.keras.layers.Dense(512, activation = "relu"),
  tf.keras.layers.Dropout(0.4),
  tf.keras.layers.Dense(256, activation="relu"),
  tf.keras.layers.Dropout(0.4),
  tf.keras.layers.Dense(64, activation="relu"),
  tf.keras.layers.Dropout(0.4),
  tf.keras.layers.Dense(32, activation="relu"),
  tf.keras.layers.Dropout(0.4),
  tf.keras.layers.Dense(1),
])

mae_percent = (sliced_data['temp'].max() - sliced_data['temp'].min()) * 10/100
print(mae_percent)

norm = (y.max() - y.min()) * 10/100
print(norm)

# callbacks
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    mae = logs.get('mae')
    val_mae_test = logs.get('val_mae')

    if(mae < norm and val_mae_test < norm):
      print("\nReached wanted accuracy!")
      self.model.stop_training = True

callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(learning_rate=1e-03, momentum=0.9)

model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(
    train_set,
    epochs = 100,
    validation_data = test_set,
    callbacks = [callbacks]
  )

mae = history.history['mae']
loss = history.history['loss']
val_mae = history.history['val_mae']
val_loss = history.history['val_loss']

fig, ax = plt.subplots(nrows = 3, figsize = (15, 10))

ax[0].plot(mae, 'r', label='MAE')
ax[0].plot(loss, 'b', label='Loss')
ax[0].set_title('MAE and Loss')
ax[0].set_xlabel('Epoch')
ax[0].set_ylabel('Value')
ax[0].legend(loc = 0)

ax[1].plot(mae, 'r', label='MAE')
ax[1].plot(val_mae, 'b', label='Val MAE')
ax[1].set_title('MAE and Val MAE')
ax[1].set_xlabel('Epoch')
ax[1].set_ylabel('Value')
ax[1].legend(loc = 0)

ax[2].plot(loss, 'r', label='Loss')
ax[2].plot(val_loss, 'b', label='Val Loss')
ax[2].set_title('Loss and Val Loss')
ax[2].set_xlabel('Epoch')
ax[2].set_ylabel('Value')
ax[2].legend(loc = 0)

plt.tight_layout()
plt.show()

predict = model.predict(test_set)

fig, ax = plt.subplots(nrows = 2, figsize=(30, 15))

ax[0].plot(predict, label="Predictions")
ax[0].set_title('Temperature Prediction Result', fontsize=20, weight='bold')
ax[0].set_xlabel('Date')
ax[0].set_ylabel('Value')
ax[0].legend(fontsize=20)

x_values = np.arange(len(x_test))

ax[1].plot(x_values, y_test, color='blue', label='Test Data')
ax[1].plot(x_values[:len(predict)], predict, color='red', label='Predictions')
ax[1].set_title('Prediction Verification vs Test Data', fontsize=20, weight='bold')
ax[1].set_xlabel('Date')
ax[1].set_ylabel('Value')
ax[1].legend(fontsize=20)

plt.show()
