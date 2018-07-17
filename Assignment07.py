# Clemens Jänicke, Humboldt-Universität zu Berlin

#While loop crashed my python every time
#but it worked at other PC'S

#from geotools import georas #needed for reprojection
import gdal
import ogr
#import struct

# #### FUNCTIONS

# #### FOLDER PATHS & global variables
wd = 'O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment07/'

# #### PROCESSING
# Reprojection
#geovec.ReprojectAndSaveNewShapefile(wd+"PrivateLands.shp",wd+"PrivateLands_proj.shp", 4326)
#geovec.ReprojectAndSaveNewShapefile(wd+"Old_Growth.shp",wd+"Old_Growth_proj.shp", 4326)
#georas.ReprojectAndSaveNewRaster(wd+"DistToRoad.tif",wd+"DistToRoad_proj.tif",4326)

# Open Shapefiles and Layers
forest = ogr.Open(wd+"Old_Growth_proj.shp")
points = ogr.Open(wd+"Points.shp")
private = ogr.Open(wd+"PrivateLands_proj.shp")
points_lyr = points.GetLayer()
private_lyr = private.GetLayer()
forest_lyr = forest.GetLayer()

# Open Rasters, Projections and GeoTransforms
roaddist = gdal.Open(wd+"DistToRoad_proj.tif")
roaddist_pr = roaddist.GetProjection
roaddist_gt = roaddist.GetGeoTransform
roaddist_rb = roaddist.GetRasterBand(1)
elev = gdal.Open(wd+"Elevation_proj.tif")
elev_pr = elev.GetProjection()
elev_gt = elev.GetGeoTransform()
elev_rb = elev.GetRasterBand(1)

extrList = [["Point ID", "Variable", "Value"]]
for point in points_lyr:
    id = point.GetField('Id')
    print(id)

    #get coordinates of point
    geom = point.GetGeometryRef()
    mx, my = geom.GetX(), geom.GetY()

    #extract elevation values
    px_elev = int((mx - elev_gt[0]) / elev_gt[1])
    py_elev = int((my - elev_gt[3]) / elev_gt[5])
    elev_value = elev_rb.ReadAsArray(px_elev, py_elev, 1, 1)[0][0]
    extrList.append([id,"Elevation",elev_value])
    print(elev_value)

    #extract distance values
    px_dist = int((mx - elev_gt[0]) / elev_gt[1])
    py_dist = int((my - elev_gt[3]) / elev_gt[5])
    dist_value = roaddist.ReadAsArray(px_elev, py_elev, 1, 1)[0][0]
    extrList.append([id,"DistToRoad",dist_value])
    print(dist_value)

    private_lyr.SetSpatialFilter(geom)
    feature_count = private_lyr.GetFeatureCount()
    if feature_count>0:
        extrList.append([id, "Private", 1])
        print("yes")
    else:
        extrList.append([id, "Private", 0])
        print("no")
    private_lyr.SetSpatialFilter(None)

    forest_lyr.SetSpatialFilter(geom)
    feature_count = forest_lyr.GetFeatureCount()
    if feature_count>0:
        extrList.append([id, "OldGrowth", 1])
        print("yes")
    else:
        extrList.append([id, "OldGrowth", 0])
        print("no")
    forest_lyr.SetSpatialFilter(None)

points_lyr.ResetReading()

import csv
#Possibility 1:
outputFile = open(wd+"extracted values3.csv", 'w')
for item in extrList:
    i=0
    for subitem in item:
        if i < 2:
            outputFile.write(str(subitem))
            outputFile.write(",")
            i += 1
        else:
            outputFile.write(str(subitem))
    outputFile.write('\n')
del outputFile

#Possibility 2: in output file is an line empty between each record
with open(wd+"extracted values.csv", "w") as csvfile:
    wr = csv.writer(csvfile)
    wr.writerows(extrList)

#feat_point = points_lyr.GetNextFeature()
#idList=[]
#elevList=[]
#while feat_point:
#    id = feat_point.GetField('Id')
#    geom = feat_point.GetGeometryRef()
#    mx,my = geom.GetX(), geom.GetY()
#    idList.append(id)
#    print(id)
#    px = int((mx - elev_gt[0]) / elev_gt[1])
#    py = int((my - elev_gt[3]) / elev_gt[5])
#    struc_var = elev_rb.ReadRaster(px, py, 1, 1)
#    elev_value = struct.unpack('H', struc_var)[0]
#    elevList.append(struc_var)
#    print(struc_var)

#    feat_point = points_lyr.GetNextFeature()
#points_lyr.ResetReading()

