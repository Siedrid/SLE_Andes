# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 14:52:00 2023

@author: obre_la
"""

# usefull functions for catchment analysis
import os
import pandas as pd

def load_catchmentData(hard_drive, catchment_name):
    os.chdir(hard_drive + ":/SLE_Anden/SLE")

    #catchment_name = '00002_Maipo-2'
    os.chdir(catchment_name)
    file_list = os.listdir()
    
    unfiltered_path = [file for file in file_list if 'raw_unfiltered' in file]
    ts_path = [file for file in file_list if 'SLE.csv' in file]
    hydro_path = [file for file in file_list if 'SLE2023' in file]
    filtered_path = [file for file in file_list if '_filtered' in file]

    SLE_ts = pd.read_csv(ts_path[0])
    unfiltered = pd.read_csv(unfiltered_path[0])
    hydrologic_year = pd.read_csv(hydro_path[0])
    filtered = pd.read_csv(filtered_path[0])
    
    SLE_ts['date'] = pd.to_datetime(SLE_ts.date)
    SLE_ts['Month'] = SLE_ts['date'].dt.month
    SLE_ts['Year'] = SLE_ts['date'].dt.year
    
    return SLE_ts, unfiltered, filtered, hydrologic_year