# co2ampel_plot.py

"""
This script gets data from the "fr_co2ampel_hft" LoRaWAN application by the
"Data Storage Integration".  The data is stored at the TTN server for 7 days.

Further information:

- https://www.thethingsnetwork.org/docs/applications/storage/api/index.html
- https://console.thethingsnetwork.org/applications/fr_co2ampel_hft/integrations
- https://fr_co2ampel_hft.data.thethingsnetwork.org
- https://fr_co2ampel_hft.data.thethingsnetwork.org/swagger.yaml

Authors:
Franz Refle, 2021 (original work)
Hubert Högl, 2021, <Hubert.Hoegl@hs-augsburg.de>
"""

import os
import requests
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
import matplotlib.dates as mdates
import pickle

url = "https://fr_co2ampel_hft.data.thethingsnetwork.org/api/v2/query/co2ampelbndlg_dev01"
args = '?last=7d'

# You need an access key to get the data. Go to 
# https://console.thethingsnetwork.org/applications/fr_co2ampel_hft
# at the bottom you see "ACCESS KEYS". Set environment variable ACCESSKEY to 
# this key with the command "export ACCESSKEY=..."
if "ACCESSKEY" not in os.environ:
    raise(ValueError('environment variable ACCESSKEY not set'))
else:
    access_key = os.environ["ACCESSKEY"]

headers = {'Accept': 'application/json', 'Authorization': 'key ' + access_key}


# Get data by Swagger UI (OpenAPI)
try:
    response = requests.get(url + args, headers=headers)
except OSError as e:
    print("Error: {0}".format(e))
    sys.exit(0)

if response.status_code == 200:
    print("Status 200, OK")
    data = response.json()
else:
    print("Error (response.status_code is {})".format(response.status_code))
    sys.exit(0)

# 'data' is a list of dicts, each entry looks like
# {'co2': 460, 'device_id': 'co2ampelbndlg_dev01', 'hum': 29, 'raw': 'F5M6',
#     'time': '2021-04-06T09:48:40.764357682Z', 'tmp': 19.40000000}


# Just a test to write data to file using the pickle module
# fo = open("data.pickle", "wb")
# pickle.dump(data, fo)
# fo.close()
# 
# Use following code to read "data.pickle" back to list L
# o = open("data.pickle", "rb")
# L = pickle.load(fo)
# fo.close()


# Time format in data: 2021-03-30T13:53:03.742880288Z 
# the 9 digit nsec fraction can not be parsed with strptime(). Cut off the last 
# four chars to get a microsecond fraction.
begin_date = data[0]['time'][:-4] 
end_date = data[-1]['time'][:-4]

fmt = "%Y-%m-%dT%H:%M:%S.%f" # %f is a 6 digit microsecond fraction
dt1 = datetime.strptime(begin_date, fmt)
dt2 = datetime.strptime(end_date, fmt)
d1 = dt1.date()
d2 = dt2.date()

df = pd.DataFrame(data)

# df DataFrame:
#    co2   device_id           hum   raw           time                   tmp
#0  1040  co2ampelbndlg_dev01  38.0  NJdM  2021-03-30T10:22:01.460562325Z 20.2
#1  1020  co2ampelbndlg_dev01  37.5  M5hL  2021-03-30T10:27:10.143553097Z 20.4
#2  1020  co2ampelbndlg_dev01  37.5  M5hL  2021-03-30T10:32:18.711297525Z 20.4
#...

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html
df['time'] = pd.to_datetime(df['time'])

ts = df.set_index('time')

# ts has 1944 rows x 5 columns
# row: time
# cols: co2, device_id, hum, raw, tmp
# print(ts)

# Pandas Plotting, see 
# User Guide https://pandas.pydata.org/docs/user_guide/
# https://pandas.pydata.org/docs/user_guide/visualization.html
# https://pandas.pydata.org/pandas-docs/version/0.23/generated/pandas.DataFrame.plot.html
#ts.plot(y='co2', grid=True)
#plt.savefig("plot_co2.jpg")

#ts.plot(y='tmp', grid=True, color='green')
#plt.savefig("plot_tmp.jpg")

#ts.plot(y='hum', grid=True, color='red')
#plt.savefig("plot_hum.jpg")

# Simple plot
# ts.plot(subplots=True)
# plt.show()

cm = 1/2.54  # inch to cm

# Place 3 subplots in one large plot on a A4 page
fig, axes = plt.subplots(3, figsize=(18*cm, 26*cm)) 
# print("fig:", type(fig), fig)

# Put format placeholders in single {...}, LaTeX commands in double {{...}}! 
fig.suptitle(r"""CO2 Sensor von Franz Refle ({begin} - {end})
   ($\it{{co2ampel\_plot.py}}$)
""".format(begin=d1, end=d2))

# ~~~ snippet from https://matplotlib.org/stable/gallery/ticks_and_spines/date_concise_formatter.html
for nn, ax in enumerate(axes):
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ['%y',  # ticks are mostly years
                         '%b',       # ticks are mostly months
                         '%d',       # ticks are mostly days
                         '%H:%M',    # hrs
                         '%H:%M',    # min
                         '%S.%f', ]  # secs
    # these are mostly just the level above...
    formatter.zero_formats = [''] + formatter.formats[:-1]
    # ...except for ticks that are mostly hours, then it is nice to have
    # month-day:
    formatter.zero_formats[3] = '%d-%b'

    formatter.offset_formats = ['',
                                '%Y',
                                '%b %Y',
                                '%d %b %Y',
                                '%d %b %Y',
                                '%d %b %Y %H:%M', ]
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    # need minor ticks at multiples of 6 hours 
    # https://www.geeksforgeeks.org/matplotlib-axis-axis-set_minor_locator-function-in-python/
    ax.xaxis.set_minor_locator(HourLocator(range(0, 25, 6)))
# ~~~

axes[0].set_title("CO2 [ppm]")
axes[1].set_title("Luftfeuchtigkeit [%]")
axes[2].set_title("Temperatur [℃]")

ts.plot(subplots=True, ax=[axes[0], axes[1], axes[2]], grid=True)

Ticks = axes[0].get_yticks()
axes[0].set_yticks(np.arange(0, 1400, 200))
Ticks = axes[0].get_yticks()
# print("Ticks[0] =", Ticks)
axes[0].yaxis.set_minor_locator(MultipleLocator(50))
axes[0].set_xlabel("") # remove "time"
# rotation not needed for concise date format
# for label in axes[0].get_xticklabels():
#    label.set_rotation(20)
#    label.set_horizontalalignment('right')

Ticks = axes[1].get_yticks()
# print("Ticks[1] =", Ticks)
axes[1].yaxis.set_minor_locator(MultipleLocator(1.0))
axes[1].set_xlabel("") # remove "time"

Ticks = axes[2].get_yticks()
# print("Ticks[2] =", Ticks)
axes[2].yaxis.set_minor_locator(MultipleLocator(1.0))
axes[2].set_xlabel("") # remove "time"

# https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.subplots_adjust.html
# wspace = width reserved, hspace = height reserved
plt.subplots_adjust(wspace=0.5, hspace=0.5)

plotfile = "plot.jpg"
plt.savefig(plotfile)
print("see", plotfile)

# plt.show()


# vim: et sw=4 ts=4
