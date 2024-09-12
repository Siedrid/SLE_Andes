# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 11:35:08 2023

@author: obre_la
"""

# Analyses for the SLE Andes Central Chile Paper

import os
from Catchment_fct import load_catchmentData
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymannkendall as mk
import rasterio as rio

hard_drive = 'D'

def plot_mk(axes, ts, month_str):
    result = mk.original_test(ts)
    print(result)
    
    trend_line = result.slope * range(len(ts.index)) + result.intercept
    #plt.figure(figsize=(8, 6))
    axes.plot(ts, label='Snow Line Data')
    axes.plot(ts.index, trend_line, color='red', label='Trend Line')
    
    axes.set_ylabel('Median SLE [m]')
    axes.set_title(month_str)
    axes.text(ts.index[1], max(ts)-200, 
             'Trend: '+ str(np.round(result.slope,2)) + ' m/year', fontsize = 10)
    axes.text(ts.index[1], max(ts)-400,
             'p-value: '+str(np.round(result.p,4)), fontsize = 10)
    plt.tight_layout()
    
SLE_ts, unfiltered, filtered, hydrologic_year = load_catchmentData(hard_drive, '00001_Aconcaqua')

#%%
JFM = [1,2,3]
JFM_df = filtered[filtered['month'].isin(JFM)]

JFM_counts = JFM_df.groupby('year')['Sensor'].value_counts().unstack().fillna(0)
#JFM_counts.plot(kind='bar', stacked=True)

JFM_med = JFM_df.groupby('year')['RSLE'].median()
JFM_mean = JFM_df.groupby('year')['RSLE'].mean()

ON = [10,11]
ON_df = filtered[filtered['month'].isin(ON)]

ON_med = ON_df.groupby('year')['RSLE'].median()
ON_mean = ON_df.groupby('year')['RSLE'].mean()

JJA = [6,7,8]
JJA_df = filtered[filtered['month'].isin(JJA)]

JJA_med = JJA_df.groupby('year')['RSLE'].median()
JJA_mean = JJA_df.groupby('year')['RSLE'].mean()

fig, ax = plt.subplots(3,1, figsize = (10,8))
plot_mk(ax[0], JFM_med, 'JFM')
plot_mk(ax[1], JJA_med, 'JJA')
plot_mk(ax[2], ON_med, 'ON')
plt.savefig(os.getcwd() + '/Plots/median_TS_MK-perseason.png', dpi = 300, bbox_inches = 'tight')

'''
result = mk.original_test(JFM_med)
print(result)

trend_line = result.slope * range(len(JFM_med.index)) + result.intercept
plt.figure(figsize=(8, 6))
plt.plot(JFM_med, label='Snow Line Data')
plt.plot(JFM_med.index, trend_line, color='red', label='Trend Line')

plt.ylabel('SLE [m]')
plt.title('Snow Line Elevation at Aconcagua Catchment')
plt.text(JFM_med.index[1], min(JFM_med)+200, 
         'Trend: '+ str(np.round(result.slope,2)) + ' m/year', fontsize = 12)
plt.text(JFM_med.index[1], min(JFM_med)+100,
         'p-value: '+str(np.round(result.p,4)), fontsize = 12)
plt.legend()

plt.show()
'''
#%% forecast

ts = ON_med    
sle = pd.Series(ts.values, index = pd.date_range(pd.to_datetime(ts.index[0], format = '%Y'), periods = len(ts.values),
                                                         freq='Y'), name = 'SLE')
sle_train = sle['1990-12-31':'2020-12-31']
lt_med = sle_train.median()

# linear Trend until 2050

result = mk.original_test(ts)
trend_line2050 = result.slope * range(2050-JFM_med.index[0]) + result.intercept
sle2050 = trend_line2050[-1]

print("SLE will be at " + str(round(sle2050,1)) + ' m in 2050')
print("SLE is normally at " + str(round(lt_med,1)) + ' m')

#%%
# load Aconcagua DEM
dem_path = 'F:/SLE_Anden/GIS/DEM/Aconcagua/DEM_Aconcagua.tif'

with rio.open(dem_path) as src:
    dem_array = src.read(1)

# count no of cells greater than the SLE
n = np.sum(dem_array > sle2050)
n_median = np.sum(dem_array > lt_med)

area = n * 0.0009 # area still covered with snow in 2050
lt_area = n_median * 0.0009

area_lost = lt_area - area
print(str(area_lost) + ' km2 of Snow extend are lost')

#%% SLE Anomalies

fig, axes = plt.subplots(3,1, figsize = (10,8))
seasons = ['JFM', 'JJA', 'ON']
for j, (series, ax) in enumerate(zip([JFM_med, JJA_med, ON_med], axes)):

    ts = series    
    sle = pd.Series(ts.values, index = pd.date_range(pd.to_datetime(ts.index[0], format = '%Y'), periods = len(ts.values),
                                                             freq='Y'), name = 'SLE')
    sle_train = sle['1990-12-31':'2020-12-31']
    lt_med = sle_train.median()
    for i, value in enumerate(series.values - lt_med):
        if value >= 0:
            ax.bar(series.index[i], value, color = 'red')
        else:
            ax.bar(ts.index[i], value, color = 'green')
        ax.set_ylabel('SLE Anomalies [m]')
        ax.set_title(seasons[j])
plt.tight_layout()
plt.savefig(os.getcwd() + '/Plots/Anomalies-perseason.png', dpi = 300, bbox_inches = 'tight')

plt.bar(ts.index, ts.values - lt_med)


#%% SLE Anomalies and SLE time series combined
# Assuming the necessary imports and the 'filtered' dataframe are already available
from pymannkendall import original_test as mk_test  # For Mann-Kendall trend test

def plot_combined(series, ax, season_label):
    # Compute SLE anomalies relative to the median
    sle = pd.Series(series.values, index=pd.date_range(pd.to_datetime(series.index[0], format='%Y'), periods=len(series.values), freq='Y'), name='SLE')
    sle_train = sle['1990-12-31':'2020-12-31']
    lt_med = sle_train.median()  # long-term median for anomalies
    
    # Create a secondary y-axis
    ax2 = ax.twinx()
    
    # Plot anomalies as bars (color based on sign of anomaly)
    anomalies = series.values - lt_med
    for i, value in enumerate(anomalies):
        if value >= 0:
            ax2.bar(series.index[i], value, color='red', alpha=0.5)
        else:
            ax2.bar(series.index[i], value, color='#D8EEFB', alpha=0.5) # spez blau ton statt grün
    
    # Perform the Mann-Kendall test and calculate the trend line
    result = mk_test(series.values)
    print(result)
    
    # Calculate the trend line based on slope and intercept
    slope = result.slope
    #intercept = np.mean(series.values) - slope * np.mean(series.index.year)
    trend_line = slope * range(len(series.index)) + result.intercept
    
    # Plot median SLE and trend line on primary y-axis
    ax.plot(series.index, series.values, label='Snow Line Elevation', color='black')
    ax.plot(series.index, trend_line, color='red', label='Trend Line')
    
    # Add annotations for slope and p-value
    ax.text(1986, max(series.values) - 100, f'Trend: {slope:.2f} m/year, \np-value: {result.p:.4f}', 
            fontsize=10, verticalalignment = "top",
            bbox=dict(facecolor='white', alpha=0.5))
    #ax.text(series.index[1], max(series.values) - 400, f'p-value: {result.p:.4f}', fontsize=10,
    #        bbox=dict(facecolor='white', alpha=0.5))
    
    # Set labels and titles
    ax.set_ylabel('Median SLE [m]')
    ax.set_title(season_label) 
    #ax.set_ylim(2000, 5200)
    
    # Configure the secondary y-axis
    ax2.set_ylabel('SLE Anomalies [m]')
    ax2.set_ylim(-1200, 1200)
    ax2.hlines(y= 0, xmin = 1985, xmax = 2023, color = 'grey')
    
    # Ensure the legend only appears on the primary axis
    ax.legend(loc='lower right') # ax2 legend dazufügen
    ax.set_xlim(1985, 2023)
    
    # Adjust grid and layout
    ax.grid(True)
    ax2.grid(False)
    plt.tight_layout()

# Create subplots for each season
fig, axes = plt.subplots(3, 1, figsize=(10, 8))
seasons = ['Jan-Feb-Mar', 'Jun-Jul-Aug', 'Oct-Nov']

# Assuming JFM_med, JJA_med, and ON_med are series objects with years as the index
for j, (series, ax) in enumerate(zip([JFM_med, JJA_med, ON_med], axes)):
    plot_combined(series, ax, seasons[j])

# Save the plot
plt.savefig(os.getcwd() + '/Plots/Anomalies-perseason_combined.png', dpi=300, bbox_inches='tight')
plt.show()

