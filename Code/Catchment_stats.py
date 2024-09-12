# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 09:29:54 2023

@author: obre_la
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import glob
import subprocess as sub
import numpy as np

# function to draw SLE shp
def DrawSL(DEM, ELE, OUTFILE):
    command = r'C:\Program Files\QGIS 3.26.1\OSGeo4W.bat gdal_contour -i 10.0 %s "%s" -fl %s' % (DEM, OUTFILE, ELE)
    # command = r'C:\OSGeo4W\OSGeo4W.bat gdal_contour -i 10.0 %s "%s" -fl %s' % (DEM, OUTFILE, ELE)

    p = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(stdout)
        print(stderr)
        
def get_elevationBand(DEM, ELE_max, ELE_min, OUT):
    
    command = r'C:\Program Files\QGIS 3.26.1\OSGeo4W.bat gdal_contour -fl %s %s -i 10.0 %s "%s" -p' % (ELE_min, ELE_max, DEM, OUT)
    p = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(stdout)
        print(stderr)

hard_drive = 'F'
os.chdir(hard_drive + ":/SLE_Anden/SLE")
def load_catchmentData(catchment_name):
    os.chdir(hard_drive + ":/SLE_Anden/SLE")

    #catchment_name = '00002_Maipo-2'
    os.chdir(catchment_name)
    file_list = os.listdir()
    
    unfiltered_path = [file for file in file_list if 'raw_unfiltered' in file]
    ts_path = [file for file in file_list if 'SLE.csv' in file]
    hydro_path = [file for file in file_list if 'SLE2023' in file]
    
    SLE_ts = pd.read_csv(ts_path[0])
    unfiltered = pd.read_csv(unfiltered_path[0])
    hydrologic_year = pd.read_csv(hydro_path[0])
    
    return SLE_ts, unfiltered, hydrologic_year

catchment_name = '00001_Aconcaqua'
#catchment_name = '00002_Maipo-2'
SLE_ts, unfiltered, hydrologic_year = load_catchmentData(catchment_name)

SLE_ts['date'] = pd.to_datetime(SLE_ts.date)
SLE_ts['Month'] = SLE_ts['date'].dt.month
SLE_ts['Year'] = SLE_ts['date'].dt.year

#%% RI, EI and RMSE plots

catchments = ['00001_Aconcaqua', '00002_Maipo-1', '00002_Maipo-2']
RI_array = np.zeros(0,)
EI_array = np.zeros(0,)
RMSE_array = np.zeros(0,)

for c in catchments:
    SLE_ts, unfiltered, hydrologic_year = load_catchmentData(c)
    RI_array = np.concatenate((RI_array, unfiltered.RI), axis = 0) 
    EI_array = np.concatenate((EI_array, unfiltered.EI), axis = 0)    
    RMSE_array = np.concatenate((RMSE_array, unfiltered.RMSE), axis = 0)    

bin_size = 0.01

fig, ax = plt.subplots(1,3, figsize=(20,6))

ax[0].grid()
ax[0].hist(RI_array, bins=int((RI_array.max() - RI_array.min()) / bin_size))
ax[0].set_xlabel('RI')
ax[0].set_ylabel('count')
ax[0].axvline(x=np.median(RI_array), color = 'red', lw = 2)
ax[0].axvline(x=np.quantile(RI_array, 0.2), color = 'grey', ls = '--', lw = 2)

# vor 0.2 abschneiden?

ax[1].grid()
ax[1].hist(EI_array, bins=int((EI_array.max() - EI_array.min()) / bin_size))
ax[1].set_xlabel('EI')
ax[1].set_ylabel('count')
ax[1].axvline(x=np.median(EI_array), color = 'red', lw = 2)
ax[1].axvline(x=np.quantile(EI_array, 0.8), color = 'grey', ls = '--', lw = 2)

ax[2].grid()
ax[2].hist(RMSE_array, bins=40)
ax[2].set_xlabel('RMSE')
ax[2].set_ylabel('count')
ax[2].axvline(x=np.nanmedian(RMSE_array), color = 'red', lw = 2)
ax[2].axvline(x=np.nanquantile(RMSE_array, 0.8), color = 'grey', ls = '--', lw = 2)

plt.savefig(os.getcwd() + '/Plots/Index_SLE.png', dpi = 300, bbox_inches = 'tight')

print('RI median = ' + str(np.median(RI_array)))
print('EI median = ' + str(np.median(EI_array)))
print('RMSE median = ' + str(np.nanmedian(RMSE_array)))

print('20th RI quantile = ' + str(np.quantile(RI_array, 0.2)))
print('80th EI quantile = ' + str(np.quantile(EI_array, 0.8)))
print('80th RMSE quantile = ' + str(np.nanquantile(RMSE_array, 0.8)))

#%% Scenes per Sensor (yearly, monthly)
# group by Month
scene_counts = unfiltered.groupby('month')['Sensor'].value_counts().unstack().fillna(0)

fig, ax = plt.subplots()
scene_counts.plot(kind = 'bar', stacked = True, ax = ax)

ax.set_xlabel('Month')
ax.set_ylabel('Count')
ax.set_title('Count of Observation per Month and Sensor for ' + catchment_name)
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/sensor_obs_monthly.png', dpi = 300, bbox_inches = 'tight')

# group by Year
scene_counts = unfiltered.groupby('year')['Sensor'].value_counts().unstack().fillna(0)

fig, ax = plt.subplots()
scene_counts.plot(kind = 'bar', stacked = True, ax = ax)

# Set axis labels and title
ax.set_xlabel('Year')
ax.set_ylabel('Count')
ax.set_title('Count of Observation per Year and Sensor')
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/sensor_obs_yearly.png', dpi = 300, bbox_inches = 'tight')

#%% monthly Box Plot of Cloud / Snow Cover

unfiltered['Snow_per'] = unfiltered['Snow'] / unfiltered['ToP']
unfiltered['Cloud_per'] = unfiltered['Cloud'] / unfiltered['ToP']

# SNOW
fig,ax = plt.subplots()
unfiltered.boxplot(column='Snow_per', by = 'month', ax = ax)

# Set axis labels and title
ax.set_xlabel('Month')
ax.set_ylabel('Snow Cover [%]')
ax.set_title('Monthly Boxplots of Snow Cover ' + catchment_name)
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/boxplot_monthly_SC.png', dpi = 300, bbox_inches = 'tight')

# CLOUD
fig,ax = plt.subplots()
unfiltered.boxplot(column='Cloud_per', by = 'month', ax = ax)

# Set axis labels and title
ax.set_xlabel('Month')
ax.set_ylabel('Cloud Cover [%]')
ax.set_title('Monthly Boxplots of Cloud Cover ' + catchment_name)
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/boxplot_monthly_CC.png', dpi = 300, bbox_inches = 'tight')



#%% SLE per month / year

# Create 'Month' column
SLE_ts['date'] = pd.to_datetime(SLE_ts.date)
SLE_ts['Month'] = SLE_ts['date'].dt.month
SLE_ts['Year'] = SLE_ts['date'].dt.year

fig,ax = plt.subplots()
SLE_ts.boxplot(column='SLE', by = 'Month', ax = ax)

# Set axis labels and title
ax.set_xlabel('Month')
ax.set_ylabel('SLE [m]')
ax.set_title('Monthly Boxplots of SLE ' + catchment_name)
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/boxplot_monthly_SLE.png', dpi = 300, bbox_inches = 'tight')

plt.figure(figsize=(20,6))
fig,ax = plt.subplots(figsize=(20,6))
SLE_ts.boxplot(column='SLE', by = 'Year', ax = ax)

# Set axis labels and title
ax.set_xlabel('Year')
ax.set_ylabel('SLE [m]')
ax.set_title('Yearly Boxplots of SLE ' + catchment_name)
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/boxplot_yearly_SLE.png', dpi = 300, bbox_inches = 'tight')

#%% Plot hydrologic year
months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 
          'May', 'Jun', 'Jul', 'Aug', 'Sep']

hydrologic_year['month_str'] = months


fig,ax = plt.subplots()
ax.plot(hydrologic_year.month_str, hydrologic_year['median'], label = 'long-term median')

if catchment_name == '00002_Maipo-2':
    years = [2022,2023]
    hydr_year = SLE_ts.loc[SLE_ts.Year.isin(years)]
    hydr_year = hydr_year.iloc[9:]
    hydr_year['month_str'] = months[0:len(hydr_year)]
    ax.plot(hydr_year.month_str, hydr_year['SLE'], label = 'SLE 2022/23')
else:
    ax.plot(hydrologic_year.month_str, hydrologic_year['SLE'], label = 'SLE 2022/23')

years = [2021,2022]
hydr_year = SLE_ts.loc[SLE_ts.Year.isin(years)]
hydr_year = hydr_year.iloc[9:21]
hydr_year['month_str'] = months
ax.plot(hydr_year.month_str, hydr_year['SLE'], label = 'SLE 2021/22')

ax.fill_between(hydrologic_year.month_str, hydrologic_year.p10, hydrologic_year.p90, alpha = 0.1,
                label = 'Interdecile Range')
ax.fill_between(hydrologic_year.month_str, hydrologic_year.p25, hydrologic_year.p75, alpha = 0.1,
                label = 'Interquartile Range')

ax.set_ylabel('SLE [m]')
ax.set_xlabel('Month')
ax.legend()
ax.set_title('Long-term SLE of ' + catchment_name)
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/hydrologic_year.png', dpi = 300, bbox_inches = 'tight')

#%% Abweichung vom langjährigen Monats-Mittel
fig, ax = plt.subplots()
ax.plot(hydrologic_year.month_str, hydrologic_year['median'])

sle_median = hydrologic_year['median']
fig, ax = plt.subplots(3,4, figsize=(15,10))
m = 1
for i in range(3):
    for j in range(4):
        
        SLE_monthly_med = SLE_ts.loc[SLE_ts.Month == m]
        med = hydrologic_year.loc[hydrologic_year.month == m]
        ax[i,j].bar(SLE_monthly_med.Year, SLE_monthly_med.SLE - med['median'].values[0])
        ax[i,j].set_title(med.month_str.values[0])
        ax[i,j].set_ylabel('SLE Difference from long-term average [m]')
            
        m+=1
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/meddif_monthly.png', dpi = 300, bbox_inches = 'tight')

#%% Time series of Max / Min SLE // Month of Max/Min SLE

SLE_ts.groupby('Year')['SLE'].max().plot()
SLE_ts.groupby('Year')['SLE'].min().plot()

#%% Compare Maipo-1 and -2 time series
catchment_name = '00002_Maipo-1'
SLE_ts_1, unfiltered_1, hydrologic_year_1 = load_catchmentData(catchment_name)
SLE_ts_1.index = pd.to_datetime(SLE_ts_1.date)


catchment_name = '00002_Maipo-2'
SLE_ts_2, unfiltered_2, hydrologic_year_2 = load_catchmentData(catchment_name)
SLE_ts_2.index = pd.to_datetime(SLE_ts_2.date)

maipo_diff = SLE_ts_2.SLE - SLE_ts_1.SLE
stdev = np.std(maipo_diff)

plt.subplots(figsize = (20,6))
plt.plot(maipo_diff)
plt.ylabel('SLE Difference [m]')
plt.title('Comparision between Maipo-1 and -2 SLE')
plt.axhline(y = 0, color = 'grey')
plt.fill_between(maipo_diff.index[60:], stdev, -stdev, alpha = 0.1, label = 'Standard deviation')
plt.legend()
plt.text(maipo_diff.index[60], -1500, 
         'Mean: '+ str(np.round(np.mean(maipo_diff),1)) + ' m', fontsize = 12)
plt.text(maipo_diff.index[60], -1800,
         'Median: '+str(np.round(np.nanmedian(maipo_diff),1))+' m', fontsize = 12)
plt.savefig(os.getcwd() + '/Plots/SLE_diffMaipo12.png', dpi = 300, bbox_inches = 'tight')


# compare long term averages
months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 
          'May', 'Jun', 'Jul', 'Aug', 'Sep']

hydrologic_year_1['month_str'] = months
hydrologic_year_2['month_str'] = months

fig,ax = plt.subplots()
ax.plot(hydrologic_year_1.month_str, hydrologic_year_1['median'], label = 'long-term median Maipo-1')
ax.plot(hydrologic_year_2.month_str, hydrologic_year_2['median'], label = 'long-term median Maipo-2')

ax.fill_between(hydrologic_year_1.month_str, hydrologic_year_1.p25, hydrologic_year_1.p75, alpha = 0.1,
                label = 'Interquartile Range Maipo-1')
ax.fill_between(hydrologic_year_2.month_str, hydrologic_year_2.p25, hydrologic_year_2.p75, alpha = 0.1,
                label = 'Interquartile Range Maipo-2')
ax.legend()
ax.set_ylabel('SLE [m]')
ax.set_title('Comparision of long-term Median of Maipo-1 and -2 catchments')
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/LTmed_Maipo-12.png', dpi = 300, bbox_inches = 'tight')


#%% STL
import matplotlib.pyplot as plt
import pandas as pd
#import seaborn as sns
from statsmodels.tsa.seasonal import STL
import statsmodels.api as sm
from pandas.plotting import register_matplotlib_converters

#register_matplotlib_converters()
#sns.set_style("darkgrid")
def plot_stl(SLE_ts):
    sle = pd.Series(SLE_ts.SLE.values, index = pd.date_range(SLE_ts.date[0], periods = len(SLE_ts.SLE.values),
                                                             freq='M'), name = 'SLE')
    #i2015 = SLE_ts.loc[SLE_ts.date == '2015-01-01'].index.values[0]
    #sle2015 = pd.Series(SLE_ts.SLE[0:i2015].values, index = pd.date_range("1-1-1985", periods = len(SLE_ts.SLE[0:i2015].values), freq='M'), name = 'SLE')
    stl = sm.tsa.seasonal_decompose(sle)
    stl = STL(sle, seasonal=13)
    res = stl.fit()
    #res.plot()
    return res, sle

#%% Mann-Kendall
import pymannkendall as mk


def plot_mk(ts):
        
    result = mk.original_test(ts)
    print(result)
    slope = result.slope
    intercept = result.intercept
    trend_line = slope * range(len(ts.index)) + intercept
    # Plot the time series with the trend line
    plt.figure(figsize=(8, 6))
    plt.plot(ts, label='Snow Line Data')
    plt.plot(ts.index, trend_line, color='red', label='Trend Line')
    
    plt.ylabel('SLE [m]')
    plt.title('Snow Line Elevation at ' + catchment_name)
    plt.text(ts.index[10], min(ts)+350, 
             'Trend: '+ str(np.round(slope * 12,2)) + ' m/year', fontsize = 12)
    plt.text(ts.index[10], min(ts)+100,
             'p-value: '+str(np.round(result.p,3)), fontsize = 12)
    plt.legend()
    
    plt.show()
    
    print('Trend of: '+ str(np.round(slope * 12,2)) + ' m/year')
    
    return result

#%% Use functions
catchment_name = '00001_Aconcaqua'
SLE_ts, unfiltered, hydrologic_year = load_catchmentData(catchment_name)
res, sle = plot_stl(SLE_ts)

res.plot()
ts = sle - res.seasonal # substract seasonal component calculated with stl from time series
ts = res.trend # use only trend component
ts = sle # use entire time series

result = plot_mk(ts)
catchments = ['00001_Aconcaqua', '00002_Maipo-1', '00002_Maipo-2']

fig,ax = plt.subplots(3,1, figsize = (16,9))
for i in range(3):
    catchment_name = catchments[i]
    SLE_ts, unfiltered, hydrologic_year = load_catchmentData(catchment_name)
    res, sle = plot_stl(SLE_ts)
    ts = res.trend # use only trend component
    
    result = mk.original_test(ts)
    
    trend_line = result.slope * range(len(ts.index)) + result.intercept
    # Plot the time series with the trend line
    ax[i].plot(sle, label='Snow Line Data')
    ax[i].plot(ts.index, trend_line, color='red', label='Trend Line')
    
    ax[i].set_ylabel('SLE [m]')
    ax[i].set_title('Snow Line Elevation at ' + catchment_name)
    ax[i].text(ts.index[10], min(sle)+400, 
             'Trend: '+ str(np.round(result.slope * 12,2)) + ' m/year', fontsize = 12)
    ax[i].text(ts.index[10], min(sle)+50,
             'p-value: '+str(np.round(result.p,3)), fontsize = 12)
    ax[i].legend()
    
fig.tight_layout()
plt.savefig(os.getcwd() + '/Plots/MK-Trend_allsites.png', dpi = 300, bbox_inches = 'tight')

#%% Forecast
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.forecasting.stl import STLForecast

idx = np.where(sle.index == '2015-01-31 00:00:00')

sle_train = sle['1985-01-31':'2015-01-31']
stlf = STLForecast(sle_train, ARIMA, model_kwargs=dict(order=(1, 1, 0), trend="t"))
stlf_res = stlf.fit()

trend_line = result.slope * range(len(ts.index)) + result.intercept

forecast = stlf_res.forecast(12*8)
plt.plot(sle, label = 'Snow Line Elevation')
plt.plot(forecast, label = 'ARIMA Forecast')
plt.plot(ts.index, trend_line, color='red', label='Trend Line')

plt.legend()
plt.title('MK-Test for ' + catchment_name)
plt.ylabel('Snow Line Elevation [m]')
plt.text(ts.index[10], min(sle)+500, 
         'Trend: '+ str(np.round(result.slope * 12,2)) + ' m/year', fontsize = 12)
plt.text(ts.index[10], min(sle)+100,
         'p-value: '+str(np.round(result.p,3)), fontsize = 12)
plt.savefig(os.getcwd() + '/Plots/MK-Trend.png', dpi = 300, bbox_inches = 'tight')

print(stlf_res.summary())
#%% calculate mean winter SLE

SLE_2021 = SLE_ts.loc[SLE_ts.date == '2022-02-01'].SLE.values[0]

# long-term median
lt_median = hydrologic_year.loc[hydrologic_year.month == 2]['median'].values[0]
# 25 and 75 percentile
p25 = hydrologic_year.loc[hydrologic_year.month == 2]['p25'].values[0]
p75 = hydrologic_year.loc[hydrologic_year.month == 2]['p75'].values[0]

# Draw SL to Shape
dem = glob.glob("*tif")[0]
# dem = 'NNTK-2_Path232.tif'

DrawSL(DEM=dem, OUTFILE='SLE_shapes/' + catchment_name +'_FEB_SLE.geojson', ELE=lt_median)
DrawSL(DEM=dem, OUTFILE='SLE_shapes/' + catchment_name +'_FEB_p25_SLE.geojson', ELE=p25)
DrawSL(DEM=dem, OUTFILE='SLE_shapes/' + catchment_name +'_FEB_p75_SLE.geojson', ELE=p75)

DrawSL(DEM=dem, OUTFILE='SLE_shapes/' + catchment_name +'_FEB2022_SLE.geojson', ELE=SLE_2021)

get_elevationBand(DEM = dem, ELE_max=p75, ELE_min=p25, OUT = 'SLE_shapes/' + catchment_name +'_quartile_range_FEB.geojson')
