from geotools import general
from geotools import georas
import ogr,os, osr
import gdal
import numpy as np

def SpatialReferenceFromRaster(ds):
    '''Returns SpatialReference from raster dataset'''
    pr = ds.GetProjection()
    sr = osr.SpatialReference()
    sr.ImportFromWkt(pr)
    return sr

os.chdir(r'C:\Users\Clemens Jänicke\Python\Uni\data\Assignment09')

wd  = "C:/Users/Clemens Jänicke/Python/Uni/data/Assignment09"

points = ogr.Open("RandomPoints.shp")
points_lyr = points.GetLayer()

fileList = general.GetFilesinFolderWithEnding(wd,".tif",True)

rasList = georas.OpenRasterFromList(fileList)

gt_list = []
for raster in rasList:
    gt = raster.GetGeoTransform()
    gt_list.append(gt)

# creates list of inverse geo transform
inv_gt_list = []
for gt in gt_list:
    inv_gt = gdal.InvGeoTransform(gt)
    inv_gt_list.append(inv_gt)

extents = [list(georas.GetCorners(x)) for x in fileList]

x_min = max([x_mins[0] for x_mins in extents])
x_max = min([x_mins[2] for x_mins in extents])
y_min = max([y_mins[1] for y_mins in extents])
y_max = min([y_mins[3] for y_mins in extents])

ras_cs = SpatialReferenceFromRaster(rasList[0])

points_cs = points_lyr.GetSpatialRef()
points_feat = points_lyr.GetNextFeature()

extrList = []
rasList1 = []
rasList2 = []
rasList3 = []
rasList4 = []
classList = []
count = 0
while points_feat:
    point = points_feat.geometry().Clone()
    point.Transform(osr.CoordinateTransformation(points_cs, ras_cs))
    mx, my = point.GetX(), point.GetY()
    if mx > x_min and mx < x_max and my > y_min and my < y_max:
        rasvalList = []
        print(point)
        classID = points_feat.GetField("Class")
        print(classID)
        for raster in rasList:
            gt = raster.GetGeoTransform()
            px = int((mx - gt[0]) / gt[1])
            py = int((my - gt[3]) / gt[5])
            rb = raster.GetRasterBand(1)
            extrValue = float(rb.ReadAsArray(px, py, 1, 1))
            rasvalList.append(extrValue)
        rasList1.append(rasvalList[0])
        rasList2.append(rasvalList[1])
        rasList3.append(rasvalList[2])
        rasList4.append(rasvalList[3])
        classList.append(classID)
        count += 1
    else:
        print("out")

    points_feat = points_lyr.GetNextFeature()
print(count)
points_lyr.ResetReading()

arr1 = np.asarray(rasList1)
arr2 = np.asarray(rasList2)
arr3 = np.asarray(rasList3)
arr4 = np.asarray(rasList4)
classArray = np.asarray(classList)

featArray = np.column_stack((arr1,arr2,arr3,arr4))
labelArray = np.reshape(classArray,(770,1))


####

extrValue = float(rb.ReadAsArray(px, py, 1, 1))
ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)


inv_gt = inv_gt_list[0]
rb = rasList[0].GetRasterBand(1)
ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
lr = gdal.ApplyGeoTransform(inv_gt, x_max, y_min)
ulx = int(ul[0])
uly = int(ul[1])
lrx = int(lr[0])
lry = int(lr[1])
# print(ulx,uly)
# print(lrx,lry)
cols = lrx - ulx
rows = lry - uly

out_array = np.zeros((cols * rows, 4), dtype=np.float64)

for i in range(len(rasList)):
    inv_gt = inv_gt_list[i]
    rb = rasList[i].GetRasterBand(1)
    #print(rb)
    ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
    lr = gdal.ApplyGeoTransform(inv_gt, x_max, y_min)
    ulx = int(ul[0])
    uly = int(ul[1])
    lrx = int(lr[0])
    lry = int(lr[1])
    #print(ulx,uly)
    #print(lrx,lry)
    cols =  lrx - ulx
    rows =  lry - uly
    print(ulx, uly)
    print(cols,rows)
    print("----")
    #arr = rb.ReadAsArray()[ulx:lrx,uly:lry]
    arr = rb.ReadAsArray(ulx,uly,cols,rows)
    #print(arr.shape)
    out_array[:, i] = arr.ravel()

outNameOutArray = "classificationDS_features_"+str(cols)+"_"+ str(rows)+".npy"
outNameLabelArray = "trainingDS_labels_"+str(cols)+"_"+ str(rows)+".npy"
outNameFeatArray = "trainingDS_features_"+str(cols)+"_"+ str(rows)+".npy"
np.save(outNameOutArray, out_array)
np.save(outNameLabelArray, labelArray)
np.save(outNameFeatArray,featArray)


