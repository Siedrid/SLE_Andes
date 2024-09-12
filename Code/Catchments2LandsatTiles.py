# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 12:52:06 2023

@author: obre_la
"""

# Convert Catchments to Landsat 8 path/row
# code adapted from Hiwi and online tutorial, see MultiPolygon_LandsatCoverage.ipynb

import sys
import os
import glob
import numpy as np
from osgeo import gdal, ogr, osr
from osgeo import gdal_array
import matplotlib.pyplot as plt
import pandas as pd
#import holoviews as hv
#from holoviews import dim, opts
from matplotlib import cm
from matplotlib import colors
import subprocess
import fiona
import geopandas as gpd
from rasterio.plot import show
import geojson
import rasterio as rio
from shapely.geometry import Polygon, LineString, MultiPoint, Point
import io
import shapely.wkt
import shapely.geometry

import urllib.request
import zipfile

# read option using geopandas
roi = gpd.read_file('D:/SLE_Anden/GIS/Catchments/level06.shp')

roi.crs
def checkPoint(feature, poly):
    geom = feature.GetGeometryRef() #Get geometry from feature
    shape = shapely.wkt.loads(geom.ExportToWkt()) #Import geometry into shapely to easily work with our point
    if shape.contains(poly):
        return True
    elif poly.overlaps(shape):
        intersection = round((poly.intersection(shape).area/poly.area)*100,2)
        return intersection
    else:
        return False

def getcover(multipolygon):

  shapefile = 'D:/SLE_Anden/GIS/WRS2_descending_0/WRS2_descending.shp'
  wrs = ogr.Open(shapefile)
  layer = wrs.GetLayer(0)

  PATH_LIST = []
  ROW_LIST = []
  C_LIST = []
  AREA_LIST = []

  PATH2_LIST = []
  ROW2_LIST = []
  AREA2_LIST = []

  PATH3_LIST = []
  ROW3_LIST = []
  AREA3_LIST = []
  
  PATH4_LIST = []
  ROW4_LIST = []
  AREA4_LIST = []
  
  for n in np.arange(len(multipolygon.geometry)):
    multipolygon = multipolygon.to_crs("EPSG:4326")
    roi = multipolygon.geometry.iloc[n]
    
    paths = []
    rows = []
    areas = []

    for i in np.arange(layer.GetFeatureCount()):
      check = checkPoint(layer.GetFeature(i), roi)
      if check != False:
          feature = layer.GetFeature(i)
          path = feature["PATH"]
          row = feature["ROW"]
          if check == True:
            area = 100
          else:
            area = check

          paths.append(path)
          rows.append(row)
          areas.append(area)

    if len(paths) > 0:
      data = {'path': paths, 'row': rows, 'area': areas}
      df = pd.DataFrame(data=data)
      df = df.sort_values(by='area', ascending=False).reset_index(drop=True)

      C_LIST.append(multipolygon['HYBAS_ID'][n]) #write Catchment ID in first column
      PATH_LIST.append(df.path[0])
      ROW_LIST.append(df.row[0])
      AREA_LIST.append(df.area[0])

      if len(paths) > 1:
        PATH2_LIST.append(df.path[1])
        ROW2_LIST.append(df.row[1])
        AREA2_LIST.append(df.area[1])
      else:
        PATH2_LIST.append(-999)
        ROW2_LIST.append(-999)
        AREA2_LIST.append(-999)
      
      if len(paths) > 2:
        PATH3_LIST.append(df.path[2])
        ROW3_LIST.append(df.row[2])
        AREA3_LIST.append(df.area[2])
      else:
        PATH3_LIST.append(-999)
        ROW3_LIST.append(-999)
        AREA3_LIST.append(-999)
        
      if len(paths) > 3:
        PATH4_LIST.append(df.path[3])
        ROW4_LIST.append(df.row[3])
        AREA4_LIST.append(df.area[3])
      else:
        PATH4_LIST.append(-999)
        ROW4_LIST.append(-999)
        AREA4_LIST.append(-999)
  
  data_out = {'id': C_LIST,'path': PATH_LIST, 'row': ROW_LIST, 'area': AREA_LIST, 
              '2nd_path': PATH2_LIST, '2nd_row': ROW2_LIST, '2nd_area': AREA2_LIST,
              '3rd_path': PATH3_LIST, '3rd_row': ROW3_LIST, '3rd_area': AREA3_LIST,
              '4th_path': PATH4_LIST, '4th_row': ROW4_LIST, '4th_area': AREA4_LIST}
  df_out = pd.DataFrame(data=data_out)

  return df_out

coverage = getcover(roi)
coverage

coverage.to_csv("D:/SLE_Anden/Tables/Landsatcoverage_v2.csv", index = False)
coverage.to_excel("D:/SLE_Anden/Tables/Landsatcoverage_v2.xlsx", index = False)
