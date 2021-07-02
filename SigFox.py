import requests
import json
import pandas as pd
import binascii
import struct
import sys
import matplotlib.pyplot as plt
from IPython.core.pylabtools import figsize
import base64
from io import BytesIO
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator)
import mpld3 



parameters = {"id": '1D9B96'}
login = "5eaa713d2564326fe5936dad"
password = "4a1b225ff4d6043114b1793f8ac74132"
authentication = (login, password)

r = requests.get("https://api.sigfox.com/v2/devices/1D9B96/messages", auth=authentication, params=parameters)
# The variable response contains the response from the server

x = r.json()
x = json.dumps(x["data"])

df = pd.read_json(x)
df['temperature'] = df['data'].str.slice(start=0, stop=8, step=1)
df['humidity'] = df['data'].str.slice(start=8, stop=16, step=1)
df['moisture'] = df['data'].str.slice(start=16, stop=20, step=1)
df['light'] = df['data'].str.slice(start=20, stop=24, step=1)

try:
    for i in range(len(df)):
        df['humidity'].values[i] = struct.unpack('<f', bytes.fromhex(df['humidity'].values[i]))[0] 
except Exception:
    pass

try:
    for i in range(len(df)):
        df['temperature'].values[i] = struct.unpack('<f', bytes.fromhex(df['temperature'].values[i]))[0] 
except Exception:
    pass

#Convert Moisture
try:
    for i in range(len(df)):
        hx = df['moisture'].values[i]
        bs = binascii.unhexlify(hx)
        padded = bs + b'\x00\x00'
        c = struct.unpack('<I', padded)
        a = int(c[0])
        df['moisture'].values[i] = a
except Exception:
    pass

#Convert Light
try:
    for i in range(len(df)):
        hx = df['light'].values[i]
        bs = binascii.unhexlify(hx)
        padded = bs + b'\x00\x00'
        c = struct.unpack('<I', padded)
        a = int(c[0])
        df['light'].values[i] = a
except Exception:
    pass

df1 = df[['device','time','data','temperature','humidity','moisture','light']]
df1.rename({'time': 'time_epoch'}, axis=1, inplace=True)
df1['timestamp'] = pd.to_datetime(df1['time_epoch'], unit='ms').dt.strftime('%d %B %Y %H:%M')
#.dt.strftime('%Y-%m-%d %H:%M:%S')

df1.drop(['time_epoch'], axis = 1)

xAchse = df1['timestamp']
yAchse = df1['temperature']

fig, ax = plt.subplots()

figsize(20, 20)
obj = plt.plot(xAchse, yAchse, color = "blue")
plt.title('Temperature over time',size = 12)
plt.xticks(rotation=90)
every_nth = 5
for n, label in enumerate(ax.xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)

plt.show()