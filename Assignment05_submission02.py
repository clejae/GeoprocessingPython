# Assignment 5
# Group Clemens Jaenicke, Jan Hemmerling, Sebastian Herwartz

import geopandas as gpd
from fiona.crs import  from_epsg
import ogr
import math
import random
import zipfile
import time


# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

# #### WORKING DIRECTORIES #### #
# Clemens/Jan:
wd = 'O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment05/'
# Basti:
#wd = 'C:/Users/Basti/Geographie/Python_SS2018/Homework_Assignments/Assignment5/Data/'

# #### FUNCTIONS #### #

def generate_pos_or_neg_int(minimum, maximum):
    return round(minimum + (maximum - minimum) * random.random())

def generate_big_poly(x_ref, y_ref):
    x1, x2, x3, x4 = x_ref - 45, x_ref - 15, x_ref + 15, x_ref + 45
    y1, y2, y3, y4 = y_ref + 45, y_ref + 15, y_ref - 15, y_ref - 45
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(x1, y1)
    ring.AddPoint(x4, y1)
    ring.AddPoint(x4, y4)
    ring.AddPoint(x1, y4)
    ring.AddPoint(x1, y1)
    big_poly = ogr.Geometry(ogr.wkbPolygon)
    big_poly.AddGeometry(ring)
    big_poly.CloseRings()
    return big_poly


# #### PROCESSING #### #

## REPROJECTION
# https://automating-gis-processes.github.io/2016/Lesson3-projections.html
points = gpd.read_file(wd+"OnePoint.shp")
points_proj = points.copy()
points_proj['geometry'] = points_proj['geometry'].to_crs(epsg=3035)
points_proj.crs = from_epsg(3035)
points_proj.to_file(wd + "OnePoint_proj.shp")
pas = gpd.read_file(wd+"WDPA_May2018_polygons_GER_select10large.shp")
pas_proj = pas.copy()
pas_proj['geometry'] = pas_proj['geometry'].to_crs(epsg=3035)
pas_proj.crs = from_epsg(3035)
pas_proj.to_file(wd + "WDPA_May2018_polygons_GER_select10large_proj.shp")

## READ REPROJECTED SHAPES ##
PA_shape = ogr.Open(wd + "WDPA_May2018_polygons_GER_select10large_proj.shp")
reference_shape = ogr.Open(wd + "OnePoint_proj.shp")
PA = PA_shape.GetLayer()
reference = reference_shape.GetLayer()

## Get the coordinates of the Referencepoint ##
gt = reference.GetExtent()
xref, yref = gt[0], gt[2] #Koordinaten der Siegessäule

## CREATE EMPTY LAYER ##
ds = ogr.Open(wd,1)
if ds.GetLayer('polygon_grid'):
    ds.DeleteLayer('polygon_grid')
    out_polygons = ds.CreateLayer('polygon_grid', PA.GetSpatialRef(), ogr.wkbPolygon)
else:
    out_polygons = ds.CreateLayer('polygon_grid', PA.GetSpatialRef(), ogr.wkbPolygon)
#add fields
out_polygons.CreateField(ogr.FieldDefn("POLYD", ogr.OFTString))
out_polygons.CreateField(ogr.FieldDefn("GROUPID", ogr.OFTString))
out_polygons.CreateField(ogr.FieldDefn("NAME", ogr.OFTString))

feature_count = 0
for feature in PA:
    miss_count = 0
    feature_count = feature_count + 1 #variable that is later used for the IDs of the polygons and groups
    geom = feature.GetGeometryRef()
    env = geom.GetEnvelope() #Get.Envelope returns minX, minY, maxX, maxY in env[0], env[2], env[1], env[3])
    name = feature.GetField('NAME')
    print(name)
    PA_xmax = math.ceil(-((xref-env[1])/30))
    PA_xmin = math.ceil(-((xref-env[0])/30))
    PA_ymax = math.ceil(-((yref - env[3]) / 30))
    PA_ymin = math.ceil(-((yref - env[2]) / 30))
    protected_poly = feature.geometry().Clone()
    count = 0
    totalcount = 0
    while (count <= 49):
        totalcount = totalcount + 1
        rand_xcoord = (generate_pos_or_neg_int(PA_xmin,PA_xmax)*30)+xref
        rand_ycoord = (generate_pos_or_neg_int(PA_ymin,PA_ymax)*30)+yref
        #print(rand_xcoord, rand_ycoord)
        poly = generate_big_poly(rand_xcoord,rand_ycoord)
        if poly.Within(protected_poly):
            xlist = [rand_xcoord - 45, rand_xcoord - 15, rand_xcoord + 15, rand_xcoord + 45]
            ylist = [rand_ycoord + 45, rand_ycoord + 15, rand_ycoord - 15, rand_ycoord - 45]
            for y in range(0, 3):
                for x in range(0, 3):
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    ring.AddPoint(xlist[x], ylist[y])
                    ring.AddPoint(xlist[x + 1], ylist[y])
                    ring.AddPoint(xlist[x + 1], ylist[y + 1])
                    ring.AddPoint(xlist[x], ylist[y + 1])
                    ring.AddPoint(xlist[x], ylist[y])
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(ring)
                    poly.CloseRings()

                    polyid = (y * 3) + x

                    out_defn = out_polygons.GetLayerDefn()  # get the layer definition
                    out_feat = ogr.Feature(out_defn)  # erzeugt ein leeres dummy-feature
                    out_feat.SetGeometry(poly)  # packt die polygone in das dummy feature
                    out_polygons.CreateFeature(out_feat)  # fügt das feature zum layer hinzu

                    out_feat.SetField(0, str(feature_count) + '.' + str(count) + '.' + str(polyid))
                    out_feat.SetField(1, str(feature_count) + '.' + str(count))
                    out_feat.SetField(2, name)
                    out_polygons.SetFeature(out_feat)
            count = count + 1
            if count < 50:
                print("Progress: " + str(count + 1) + "/50")
            else:
                print("Ready")
        else:
            miss_count = miss_count + 1
            pass
    print("Miss rate: "+ str(miss_count)+ "/" + str(totalcount))
PA.ResetReading()

ds = None

# Save as KML File
shape = ogr.Open('O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment05/polygon_grid.shp')
layer = shape.GetLayer()

driver = ogr.GetDriverByName('KML')
KMLout = driver.CreateDataSource('O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment05/polygon_grid.kml')
KMLlayer = KMLout.CreateLayer('polygons', layer.GetSpatialRef(), ogr.wkbPolygon)

KMLlayer.CreateFields(layer.schema)

out_feat = ogr.Feature(KMLlayer.GetLayerDefn())

for in_feat in layer:
    geom = in_feat.geometry().Clone()
    out_feat.SetGeometry(geom)
    for i in range(in_feat.GetFieldCount()):
        out_feat.SetField(i, in_feat.GetField(i))
    KMLlayer.CreateFeature(out_feat)
KMLout.Destroy()
del shape

### Save Files in ZipFile
#import zipfile
zipp = zipfile.ZipFile(wd+'3x3polygons.zip', mode='w')
zipp.write(wd+'polygon_grid.shx')
zipp.write(wd+'polygon_grid.shp')
zipp.write(wd+'polygon_grid.prj')
zipp.write(wd+'polygon_grid.dbf')
zipp.close()

# #### END TIME-COUNT AND PRINT TIME STATS #### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")