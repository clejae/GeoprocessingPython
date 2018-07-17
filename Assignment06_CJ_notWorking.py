# Clemens Jänicke, Humboldt-Universität zu Berlin

### Hi Matthias,
# ich habe mich ziemlich verrrant in meinen Überlegungen und habe das mit dem Stacken der Windows etwas falsch verstanden.
# Inzwischen weiß ich, wie ich die Slices hätten stacken müssen, aber immer wenn ich apply_alon_axis laufen lasse, dann rechnet es ewig.
# Da die Zeit inzwischen sehr fortgeschritten ist und ich morgen nicht in Berlin bin, muss ich dir leider ein nicht laufendes Script abgeben und habe keine Ergebnisse vorzuweisen.
# Das hier ist die ursprüngliche Version mit all meinen Denkfehlern drin.

import time
import gdal
import os
from osgeo import gdal
import numpy as np
import math
from math import log

# #### FOLDER PATHS & global variables #### #
wd = 'O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment06/'
radList =[150,300,450]
classList = [1,2,3,5,11,13,17,18,19]

# #### Functions
def GetFilesinFolderWithEnding(folder, ext, fullPath):
    outlist = []
    input_list = os.listdir(folder)
    if fullPath == True:
        for file in input_list:
            if file.endswith(ext):
                if folder.endswith("/"):
                    filepath = folder + file
                else:
                    filepath = folder + "/" + file
                outlist.append(filepath)
    if fullPath == False or fullPath == None:
        for file in input_list:
            if file.endswith(ext):
                outlist.append(file)
    if len(outlist) == 1:
        print("Found only one file matching the extension. Returning a variable instead of a list")
        outlist = outlist[0]
    if len(outlist) == 0:
        print("Could not find any file matching the extension. Return-value is None")
    return outlist

def stack_moving_windows_of_array(pxRes, array, rasYdim, rasXdim):
    outArray = np.zeros(((rasYdim-pxRes+1)*(rasXdim-pxRes+1), pxRes, pxRes))
    count = 0
    for y in range(0, len(array[0]) - pxRes+1):
        for x in range(0, len(array) - pxRes+1):
            arr_sub = array[x: x + pxRes, y: y + pxRes].copy()
            outArray[count] = arr_sub
            count += 1
    return outArray

def shannon(array): #,classvalueList): #adapted function so that it can be applied with apply along axis
    from math import log
    classList = [1, 2, 3, 5, 11, 13, 17, 18, 19] #remove later
    shdi = 0
    for classvalue in classList:
        classProp=len(array[array == classvalue])/array.size
        if classProp != 0:
            shdi = (shdi + (classProp*log(classProp)))
        shdi = shdi*-1
    return shdi

# #### Processing

tifList = GetFilesinFolderWithEnding(wd, "tif", False)
rasterList = []

for tif in tifList:
    raster = gdal.Open(wd+tif)
    rasterList.append(raster)

gtList = [] # top left x, w-e pixel resolution, 0, top left y, 0, n-s pixel resolution (negative value)
prList = []
colsList = []
rowsList = []
nbandsList = []

for raster in rasterList:
    gt = raster.GetGeoTransform()
    pr = raster.GetProjection()
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    gtList.append(gt)
    prList.append(pr)
    colsList.append(cols)
    rowsList.append(rows)

rbList = []
for raster in rasterList:
    rb = raster.GetRasterBand(1)
    rbList.append(rb)

arrList = []
for i in range(0, len(rasterList)):
    rb = rbList[i]
    cols = colsList[i]
    rows = rowsList[i]
    array = rb.ReadAsArray(0,0, cols, rows)
    arrList.append(array)

testArray = arrList[0]

def make_slices(data, win_size):
    """Return a list of slices given a window size.
    data     - two-dimensional array to get slices from
    win_size - tuple of (rows, columns) for the moving window
    """
    rows = data.shape[0] - win_size[0] + 1
    cols = data.shape[1] - win_size[1] + 1
    slices = []
    for i in range(win_size[0]):
        for j in range(win_size[1]):
            slices.append(data[i:rows + i, j:cols + j])
    return slices

def shannon(array,classvalueList):
    from math import log
    shdi = 0
    for classvalue in classList:
        classProp=len(array[array == classvalue])/array.size
        if classProp != 0:
            shdi = (shdi + (classProp*log(classProp)))
        shdi = shdi*-1
    return shdi

testSlices = make_slices(testArray,(11,11))
testStack = np.ma.dstack(testSlices)




drvR = gdal.GetDriverByName('GTiff')
i = 0
for array in arrList:
    for radius in radList:
        pxRes = int((radius * 2 + gtList[i][1]) / gtList[i][1])
        ResultArray = np.zeros(shape=(rowsList[i], colsList[i]), dtype=np.float)
        inArraySlices = stack_moving_windows_of_array(pxRes, array, rowsList[i], colsList[i])
        #ResultArray = np.apply_along_axis(shannon(classList, arrList[i]), 2, inArraySlices)
        for rows in range(math.floor(pxRes/2), rowsList[i]-math.ceil(pxRes/2)):
           for columns in range(math.floor(pxRes/2), colsList[i]-math.ceil(pxRes/2)):
                ResultArray[rows, columns] = np.apply_along_axis(shannon(classList), 2, inArraySlices)
        outRaster = drvR.Create(wd+"Shannon/shdi_rad"+radius+"_"+tifList[i],colsList[i],rowsList[i], gdal.GDT_Float32)
        outRaster.SetProjection(prList[i])
        outRaster.SetGeoTransform(gtList[i])
        outRaster.GetRasterBand(1).WriteArray(ResultArray, 0, 0)
        outRaster = None
    i = i+1


