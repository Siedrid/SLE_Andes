# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:12:51 2023

@author: obre_la
"""
import os
hard_drive = 'D'
os.chdir(hard_drive + ":/SLE_Anden/Python/Code")
from Catchment_fct import load_catchmentData
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

catchment_name = '00001_Aconcaqua'
SLE_ts, unfiltered, hydrologic_year = load_catchmentData('D', catchment_name)
SLE_ts['date'] = pd.to_datetime(SLE_ts.date)
SLE_ts['Month'] = SLE_ts['date'].dt.month
SLE_ts['Year'] = SLE_ts['date'].dt.year
SLE_ts.index = pd.to_datetime(SLE_ts.date)

# Preparing Climate Data
## SOI
os.chdir(hard_drive + ":/SLE_Anden/Climate_data")
soi = pd.read_csv('SOI_edited.txt', sep = "\s+")

df = pd.melt(soi, id_vars = 'YEAR', var_name='Month', value_name='SOI')
df['Date'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['Month'])

df = df.sort_values(by='Date')

df.index = df.Date
#df = df.drop(columns=['YEAR', 'Date'])

df['SOI'] = df['SOI'].replace(-999.9, np.nan)
df.plot()


# relevant is only data from 1990 to June 2023
soi_rel = df['1985-01-01': '2023-06-01']
plt.scatter(SLE_ts.SLE, soi_rel.SOI)
soi_rel.SOI.corr(SLE_ts.SLE)


# only February obs
soi_feb = soi_rel.loc[soi_rel.Month == 'FEB']
SLE_feb = SLE_ts.loc[SLE_ts.Month == 2]
plt.scatter(SLE_feb.SLE, soi_feb.SOI)

#%% El NINO SST Anomalies

sst = pd.read_csv('nino_sst_anomalies.txt', sep = "\s+")
sst['Date'] = pd.to_datetime(sst['YR'].astype(str) + '-' + sst['MON'].astype(str))

# SST
sst.index = sst.Date
nino12 = sst['1985-01-01':'2023-06-01']['NINO1+2']

co_coeff = nino12.corr(SLE_ts.SLE)
slope, intercept = np.polyfit(SLE_ts.SLE, nino12, 1)
regression_line = slope * SLE_ts.SLE + intercept

plt.scatter(SLE_ts.SLE, nino12)
plt.plot(SLE_ts.SLE, regression_line, color = 'red', label = 'Regression line')
plt.xlabel("SLE [m]")
plt.ylabel('SST [°C]')
plt.title("Correlation of Nino 1+2 SST with SLE at " + catchment_name)
plt.text(1450, 28, "Correlation Coefficient: " + str(np.round(co_coeff, 3)))
plt.savefig(os.getcwd() + '/Plots/SST_corr.png', dpi = 300, bbox_inches = 'tight')


# SST Anomalies
anom = sst['1985-01-01':'2023-06-01']['ANOM']
plt.scatter(SLE_ts.SLE, anom)
anom.corr(SLE_ts.SLE)

# only JFM:
JFM_sst = sst[sst['MON'].isin([1,2,3])]
JFM_sst = JFM_sst.groupby('YR')['ANOM'].mean().reset_index()
JFM_sst.index = pd.to_datetime(JFM_sst.YR, format = "%Y")
JFM_sst = JFM_sst['1985-01-01':'2023-01-01']
plt.bar(JFM_sst.index, JFM_sst.ANOM.values)

max_SLE = SLE_ts.groupby('Year')['SLE'].max()

plt.scatter(max_SLE, JFM_sst.ANOM)

#%% SAM
os.chdir("F:/SLE_Anden/Climate_data")
sam = pd.read_csv('SAM.txt', sep = "\s+", names = soi.columns)

SAM = pd.melt(sam, id_vars = 'YEAR', var_name='Month', value_name='SAM')
SAM['Date'] = pd.to_datetime(SAM['YEAR'].astype(str) + '-' + SAM['Month'])

SAM = SAM.sort_values(by='Date')
SAM.index = SAM.Date
SAM = SAM['1990-01-01':]
SLE_ts2011 = SLE_ts['1990-01-01': '2011-12-01']
plt.scatter(SAM.SAM, SLE_ts2011.SLE)

SAM.SAM.corr(SLE_ts2011.SLE)

fig, ax1 = plt.subplots(figsize = (20,6))
ax1.plot(SLE_ts2011.date, SLE_ts2011.SLE, color = 'blue', label = "Snow Line Elevation")
ax1.set_ylabel('SLE [m]')

ax2 = ax1.twinx()

ax2.plot(SAM.Date, SAM.SAM)
ax2.set_ylabel('SAM')
ax2.set_ylim(-4, 10)
