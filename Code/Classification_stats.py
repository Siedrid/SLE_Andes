# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 12:44:30 2023

@author: obre_la
"""

# Timeseries of Cloud Cover over LS Tiles - NUNATAK

import numpy as np,os,sys
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from datetime import datetime
import rasterio as rio
import pandas as pd

hard_drive = 'D'
os.chdir(hard_drive + ":/SLE_Anden/classifications")

pathrow = os.listdir()[0]
os.chdir(pathrow)

date_lst = []
snowfree_pixel = []
snow_pixel = []
cloud_pixel = []
water_pixel = []

scene_lst = os.listdir()

for scene in scene_lst:
    
    date_str = scene.split('_')[3]
    date_lst.append(datetime.strptime(date_str, '%Y%m%d'))
    
    ds = rio.open(scene)
    snow_class = ds.read(1)
    unique, counts = np.unique(snow_class, return_counts=True)
    
    idx = np.where(unique == 10)
    snowfree_pixel.append(counts[idx][0])
    
    idx = np.where(unique == 11)
    snow_pixel.append(counts[idx][0])
    
    idx = np.where(unique == 12)
    cloud_pixel.append(counts[idx][0])
    
    idx = np.where(unique == 15)
    water_pixel.append(counts[idx][0])

# write to csv
df = pd.DataFrame({'date': date_lst, 'snow_free': snowfree_pixel, 'snow': snow_pixel,
             'cloud': cloud_pixel, 'water': water_pixel})

df.to_csv('F:/SLE_Anden/Tables/Classification_stats/TSbyClasses_' + pathrow + '.csv', sep = ',')

#%% Plot some time series
path_to_plots = hard_drive + ':/SLE_Anden/Plots/Classification/Statistics'

os.chdir(hard_drive + ":/SLE_Anden/Tables/Classification_stats")
df = pd.read_csv(os.listdir()[0], index_col = 'date')
df = df.iloc[0:,1:]
df.index = [datetime.strptime(date, '%Y-%m-%d') for date in df.index ]

pixel_sum = df.sum(axis = 1).values
df_per = pd.DataFrame({'snow_free' : (df.snow_free / pixel_sum),
                       'snow' : (df.snow / pixel_sum), 'cloud' : (df.cloud / pixel_sum),
                       'water' : (df.water /pixel_sum)})

df_per['Date'] = pd.to_datetime(df_per.index)
df_sorted = df_per.sort_values(by = 'Date')


plt.figure(figsize=(20,6))
plt.plot(df_sorted.index, df_sorted.snow_free)
plt.title("Time series of percentage of Snow free Pixel")
plt.ylabel("Percentage")
plt.tight_layout()
plt.savefig(path_to_plots + '/timeseries_snowfree.png', dpi = 300, bbox_inches = 'tight')

plt.figure(figsize=(20,6))
plt.plot(df_sorted.index, df_sorted.cloud)
plt.title("Time series of percentage of Cloud covered Pixel")
plt.ylabel("Percentage")
plt.tight_layout()
plt.savefig(path_to_plots + '/timeseries_cloud.png', dpi = 300, bbox_inches = 'tight')

#%% monthly Box Plot of Cloud / Snow Cover

# Create 'Month' column
df_per['Month'] = df_per['Date'].dt.month
df_per['Year'] = df_per['Date'].dt.year

fig,ax = plt.subplots()
df_per.boxplot(column='snow', by = 'Month', ax = ax)

# Set axis labels and title
ax.set_xlabel('Month')
ax.set_ylabel('Snow Cover [%]')
ax.set_title('Monthly Boxplots of Snow Cover ' + pathrow)
fig.tight_layout()
plt.savefig(path_to_plots + '/boxplot_monthly_SC.png', dpi = 300, bbox_inches = 'tight')

#%% Scenes per Sensor (yearly, monthly)

os.chdir(hard_drive + ":/SLE_Anden/classifications")

pathrow = os.listdir()[0]
os.chdir(pathrow)
scene_lst = os.listdir()

sensor_lst = [scene_str.split('_')[0] for scene_str in scene_lst]

# group by Month
scene_df = pd.DataFrame({'Sensor': sensor_lst, 'Month': df_per.Month})
scene_counts = scene_df.groupby('Month')['Sensor'].value_counts().unstack().fillna(0)

fig, ax = plt.subplots()
scene_counts.plot(kind = 'bar', stacked = True, ax = ax)

# Set axis labels and title
ax.set_xlabel('Month')
ax.set_ylabel('Count')
ax.set_title('Count of Observation per Month and Sensor')
fig.tight_layout()
plt.savefig(path_to_plots + '/sensor_obs_monthly.png', dpi = 300, bbox_inches = 'tight')

# group by Year
scene_df = pd.DataFrame({'Sensor': sensor_lst, 'Year': df_per.Year})
scene_counts = scene_df.groupby('Year')['Sensor'].value_counts().unstack().fillna(0)

fig, ax = plt.subplots()
scene_counts.plot(kind = 'bar', stacked = True, ax = ax)

# Set axis labels and title
ax.set_xlabel('Year')
ax.set_ylabel('Count')
ax.set_title('Count of Observation per Year and Sensor')
fig.tight_layout()
plt.savefig(path_to_plots + '/sensor_obs_yearly.png', dpi = 300, bbox_inches = 'tight')

