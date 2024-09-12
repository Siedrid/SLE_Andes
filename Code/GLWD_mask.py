# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 10:19:25 2023

@author: obre_la
"""

# Clip GLWD to extent of the Andes


inshp = 'D:/SLE_Anden/GIS/Mtn_classification/Anden_total.shp'
inRas = 'D:/SLE_Anden/GIS/Global Lakes and Wetlands Database/GLWDclass7_pans.tif'
outRas = '/D:/SLE_Anden/GIS/Global Lakes and Wetlands Database/GLWDclass7_pans_clipped.tif'

from osgeo import gdal, gdalconst
harddrive = 'F:'

inputpath = harddrive + "/SLE_Anden/GIS/Global Lakes and Wetlands Database/GLWDclass7_pans_AndesUTM.tif"
inputFile = gdal.Open(inputpath, 0)
inputProj = inputFile.GetProjection()
inputTrans = inputFile.GetGeoTransform()

# open reference file and get resolution
referenceFile = harddrive + "/SLE_Anden/Daten/LC08_L2SP_233074_20210824_20210901_02_T1/LC08_L2SP_233074_20210824_20210901_02_T1_SR_B2.TIF"
reference = gdal.Open(referenceFile, 0)  # this opens the file in only reading mode
referenceProj = reference.GetProjection()
referenceTrans = reference.GetGeoTransform()
bandreference = reference.GetRasterBand(1)
x_res = reference.RasterXSize
y_res = reference.RasterYSize  # make sure this value is positive

# specify input and output filenames
outputFile = harddrive +"/SLE_Anden/GIS/Global Lakes and Wetlands Database/GLWDclass7_pans_Andes_resampled.tif"
driver= gdal.GetDriverByName('GTiff')
output = driver.Create(outputFile, x_res, y_res)
output.SetGeoTransform(referenceTrans)
output.SetProjection(referenceProj)

gdal.ReprojectImage(input, output, inputProj, referenceProj, gdalconst.GRA_Bilinear)


from osgeo import gdal
driver = 'F:'

# open reference file and get resolution
referenceFile = driver + "/SLE_Anden/Daten/LC08_L2SP_233074_20210824_20210901_02_T1/LC08_L2SP_233074_20210824_20210901_02_T1_SR_B2.TIF"
reference = gdal.Open(referenceFile, 0)  # this opens the file in only reading mode
referenceTrans = reference.GetGeoTransform()
x_res = referenceTrans[1]
y_res = -referenceTrans[5]  # make sure this value is positive

# specify input and output filenames
inputFile = driver + "/SLE_Anden/GIS/Global Lakes and Wetlands Database/GLWDclass7_pans_AndesUTM.tif"
outputFile = driver +"/SLE_Anden/GIS/Global Lakes and Wetlands Database/GLWDclass7_pans_Andes_resampled.tif"

# call gdal Warp
kwargs = {"format": "GTiff", "xRes": x_res, "yRes": y_res}
ds = gdal.Warp(outputFile, inputFile, **kwargs)