# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 08:52:51 2023

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
    
    command = r'C:\OSGeo4W\OSGeo4W.bat gdal_contour -fl %s %s -i 10.0 %s "%s" -p' % (ELE_min, ELE_max, DEM, OUT)
    p = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(stdout)
        print(stderr)
        
os.chdir("D:/SLE_Anden/GIS/Catchments/SLE-Ableitung/Maipo")

out_path = "Snowdef_2050_Maipo-1.geojson"

get_elevationBand("Maipo-1_DEM.tif", sle2050, lt_med, out_path)
