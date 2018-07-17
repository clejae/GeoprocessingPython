# ##### LOAD REQUIRED LIBRARIES

import gdal
import os
import ogr, osr
import time
import numpy as np
import math

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# #### FUNCTIONS
def TransformGeometry(geometry, target_sref):
    '''Returns cloned geometry, which is transformed to target spatial reference'''
    geom_sref= geometry.GetSpatialReference()
    transform = osr.CoordinateTransformation(geom_sref, target_sref)
    geom_trans = geometry.Clone()
    geom_trans.Transform(transform)
    return geom_trans

def SpatialReferenceFromRaster(ds):
    '''Returns SpatialReference from raster dataset'''
    pr = ds.GetProjection()
    sr = osr.SpatialReference()
    sr.ImportFromWkt(pr)
    return sr

def CopySHPDisk(layer, outpath):                        #not necessarily needed
    drvV = ogr.GetDriverByName('ESRI Shapefile')
    outSHP = drvV.CreateDataSource(outpath)
    lyr = layer
    sett90LYR = outSHP.CopyLayer(lyr, 'lyr')
    del lyr, sett90LYR, outSHP

def CopyToMem(path):
    drvMemV = ogr.GetDriverByName('Memory')
    f_open = drvMemV.CopyDataSource(ogr.Open(path),'')
    return f_open

# ####FOLDER PATHS & global variables
wd = "C:/Users/Clemens Jänicke/Python/Uni/data/Assignment08/"

# #### FUNCTIONS
# Raster
dem = gdal.Open(wd+"DEM_Humboldt.tif")
gt = dem.GetGeoTransform()
pr = dem.GetProjection()
sr_raster = SpatialReferenceFromRaster(dem)

# Vector
drv = ogr.GetDriverByName('ESRI Shapefile')
parcels = ogr.Open(wd + "Parcels.shp")
#parcels = CopyToMem(wd + "Parcels.shp")
public = ogr.Open(wd + "PublicLands.shp")
marihuana = ogr.Open(wd + "Marihuana_Grows.shp")
roads = ogr.Open(wd + "Roads.shp", 1)
thp = ogr.Open(wd + "TimberHarvestPlan.shp", 1)

roads_lyr = roads.GetLayer()
thp_lyr = thp.GetLayer()
marihuana_lyr = marihuana.GetLayer()
parcels_lyr = parcels.GetLayer()
public_lyr = public.GetLayer()

parcels_cs = parcels_lyr.GetSpatialRef()
marihuana_cs = marihuana_lyr.GetSpatialRef()
public_cs = public_lyr.GetSpatialRef()

parcels_def = parcels_lyr.GetLayerDefn()

# Set filter for relevant road types and relevant years
roads_lyr.SetAttributeFilter("FUNCTIONAL IN ('Local Roads', 'Private')")
thp_lyr.SetAttributeFilter("THP_YEAR = '1999'")

# Create output dataframe
#out_df = pd.DataFrame(columns=["Parcel APN", "NR_GH-Plants", "NR_OD-Plants", "Dist_to_grow_m", "Km Local Road", "Km Priv. Road", "Prop_in_THP", "Mean elevation", "PublicLand_YN"])
outList = [["Parcel APN", "NR_GH-Plants", "NR_OD-Plants", "Dist_to_grow_m", "Km Local Road", "Km Priv. Road", "Prop_in_THP", "Mean elevation", "PublicLand_YN"]]

parcel_feat = parcels_lyr.GetNextFeature()
id = 0
while parcel_feat:
    id += 1
    apn = parcel_feat.GetField('APN')
    print("ID: " + str(id) + " APN: " + apn)

    parcel = parcel_feat.geometry().Clone()

    # 1
    parcel.Transform(osr.CoordinateTransformation(parcels_cs, marihuana_cs))
    marihuana_lyr.SetSpatialFilter(parcel)

    total_gh = total_od = 0

    point_feat = marihuana_lyr.GetNextFeature()
    while point_feat:
        total_gh += point_feat.GetField('g_plants')
        total_od += point_feat.GetField('o_plants')
        point_feat = marihuana_lyr.GetNextFeature()
    marihuana_lyr.ResetReading()

    # 2
    feature_count = marihuana_lyr.GetFeatureCount()
    if feature_count > 0:
        marihuana_lyr.SetSpatialFilter(None)
        bufferSize = 0
        exit = 0
        while exit == 0:
            bufferSize = bufferSize + 10
            buffer = parcel.Buffer(bufferSize)
            marihuana_lyr.SetSpatialFilter(buffer)
            buffer_count = marihuana_lyr.GetFeatureCount()
            if buffer_count > feature_count:
                exit += 1
                distance = bufferSize
    else:
        distance = 'NA'
    marihuana_lyr.SetSpatialFilter(None)

    # 3
    geom = parcel_feat.GetGeometryRef()

    # loop through two categories
    road_feat = roads_lyr.GetNextFeature()
    local_length = private_length = 0

    while road_feat:
        functional = road_feat.GetField('FUNCTIONAL')
        geom_roads = road_feat.GetGeometryRef()
        intersection = geom.Intersection(geom_roads)        # calculate intersection of road types and individual parcel
        length = intersection.Length()                      # get length of intersection
        if functional == "Local Roads":
            local_length = length/1000
        if functional == "Private":
            private_length = length/1000
        road_feat = roads_lyr.GetNextFeature()
    roads_lyr.ResetReading()

    # timber harvest plan > only use one year (overlapping geometries)
    thp_lyr.SetSpatialFilter(geom)                  # Set filter for parcel
    thp_feat = thp_lyr.GetNextFeature()
    area_parcel = geom.GetArea()                    # area of parcel
    thp_list = []
    # loop through selected features
    while thp_feat:
        geom_thp = thp_feat.GetGeometryRef()
        intersect_thp = geom.Intersection(geom_thp) # intersection of parcel and selected thp features
        area = intersect_thp.GetArea()              # area of intersected thp feature
        thp_list.append(area)                       # add area of thp feature to list
        thp_feat = thp_lyr.GetNextFeature()
    thp_lyr.ResetReading
    thp_sum = sum(thp_list)                         # sum up all thp features in parcel
    thp_prop = thp_sum/area_parcel

    #4
    parcels_geom_trans = TransformGeometry(geom, sr_raster)
    x_min, x_max, y_min, y_max = parcels_geom_trans.GetEnvelope()

    # # Create dummy shapefile to stor features geometry in (necessary for rasterizing)
    drv_mem = ogr.GetDriverByName('Memory')
    ds = drv_mem.CreateDataSource("")
    ds_lyr = ds.CreateLayer("", SpatialReferenceFromRaster(dem), ogr.wkbPolygon)
    featureDefn = ds_lyr.GetLayerDefn()
    out_feat = ogr.Feature(featureDefn)
    out_feat.SetGeometry(parcels_geom_trans)
    ds_lyr.CreateFeature(out_feat)
    out_feat = None
    # # CopySHPDisk(ds_lyr, "tryout.shp") #If you wish to check the shp

    # # Create the destination data source
    x_res = math.ceil((x_max - x_min) / gt[1])
    y_res = math.ceil((y_max - y_min) / gt[1])
    target_ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, gdal.GDT_Byte)
    target_ds.GetRasterBand(1).SetNoDataValue(-9999)
    target_ds.SetProjection(pr)
    target_ds.SetGeoTransform((x_min, gt[1], 0, y_max, 0, gt[5]))

    # # Rasterization
    gdal.RasterizeLayer(target_ds, [1], ds_lyr, burn_values=[1])#, options=['ALL_TOUCHED=TRUE'])
    target_array = target_ds.ReadAsArray()
    # # target_ds = None

    # # Convert data from the DEM to the extent of the envelope of the polygon (to array)
    inv_gt = gdal.InvGeoTransform(gt)
    offsets_ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
    off_ul_x, off_ul_y = map(int, offsets_ul)
    raster_np = np.array(dem.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, x_res, y_res))

    # # Calculate the mean of the array with masking
    test_array = np.ma.masked_where(target_array < 1, target_array)
    raster_masked = np.ma.masked_array(raster_np, test_array.mask)
    dem_mean = np.mean(raster_masked)

    parcel.Transform(osr.CoordinateTransformation(parcels_cs, public_cs))
    public_lyr.SetSpatialFilter(geom)
    public_out = 0
    public_count = public_lyr.GetFeatureCount()

    if public_count > 0:
        public_out = 1
    public_lyr.SetSpatialFilter(None)
    print("Public out: ", public_out, " Public count: ", public_count)

    # Output
    outList.append([apn, total_gh, total_od, distance, local_length, private_length, thp_prop, dem_mean, public_out])

    parcel_feat = parcels_lyr.GetNextFeature()
parcels_lyr.ResetReading()

import csv
outputFile = open(wd+"_out01.csv", 'w')
for item in outList:
    i=0
    for subitem in item:
        if i < len(outList[0])-1:
            outputFile.write(str(subitem))
            outputFile.write(",")
            i += 1
        else:
            outputFile.write(str(subitem))
    outputFile.write('\n')
del outputFile

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + starttime)
print("end: " + endtime)