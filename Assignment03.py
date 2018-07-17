# Clemens Jänicke, Humboldt-Universität zu Berlin


# #### LOAD REQUIRED LIBRARIES #### #
import time
import os
from osgeo import gdal
import numpy as np
from scipy import stats

# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

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

def GetCorners(path):
    ds = gdal.Open(path)
    gt = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    return minx, miny, maxx, maxy

# #### FOLDER PATHS & global variables #### #
wd = 'O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/'



# #### PROCESSING #### #

#EXERCISE 1.1: SUMMARY STATISTICS
# COMMON EXTENT
# Note to myself: GetFilesinFolderWithEnding does not work somehow. Find the problem later!
#tifList = GetFilesinFolderWithEnding(wd, "tif", fullPath=True)
tifListDummy = ["O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/DEM_Humboldt_sub.tif","O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/SLOPE_Humboldt_sub.tif","O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/THP_Humboldt_sub.tif"]
extents = [list(GetCorners(x)) for x in tifListDummy]

x_min = max([x_mins[0] for x_mins in extents])
x_max = min([x_mins[2] for x_mins in extents])
y_min = max([y_mins[1] for y_mins in extents])
y_max = min([y_mins[3] for y_mins in extents])

print('lower left X: ' + str(x_min) + " Y:" + str(y_min))
print('upper left X: ' + str(x_min) + " Y:" + str(y_max))
print('upper right X: ' + str(x_max) + " Y:" + str(y_max))
print('lower right X: ' + str(x_max) + " Y:" + str(y_min))

# LOAD RASTER DATA
dem = gdal.Open("O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/DEM_Humboldt_sub.tif")
slope = gdal.Open("O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/SLOPE_Humboldt_sub.tif")
thp = gdal.Open("O:/Student_Data/CJaenicke/04_SoSe_18/GeoPython/data/Assignment03/THP_Humboldt_sub.tif")
raster_list = [dem,slope,thp]
dem = None
slope = None
thp = None

# creates list of geo transform
gt_list = []
for raster in raster_list:
    gt = raster.GetGeoTransform()
    gt_list.append(gt)

# creates list of inverse geo transform
inv_gt_list = []
for gt in gt_list:
    inv_gt = gdal.InvGeoTransform(gt)
    inv_gt_list.append(inv_gt)

# transforms geocoordinates into pixel locations of the rasters
# saves pixel locations in lists
ul_list = []
ll_list = []
ur_list = []
lr_list = []
for inv_gt in inv_gt_list:
    ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
    ll = gdal.ApplyGeoTransform(inv_gt, x_min, y_min)
    ur = gdal.ApplyGeoTransform(inv_gt, x_max, y_max)
    lr = gdal.ApplyGeoTransform(inv_gt, x_max, y_min)
    ul_list.append(ul)
    ll_list.append(ll)
    ur_list.append(ur)
    lr_list.append(lr)

# rounding of all values in the various lists
coord_list = [ul_list, ll_list, ur_list, lr_list] #creates list of lists
coord_list_round = [] # 1. level: ul, ll, ur, lr. 2. level: dem, slope, thp. 3. level: x, y
for list in coord_list: #iterates through every list
    list_array = np.array(list) #transforms list to array
    list_array.round(0, out=list_array) #rounds all values in array
    list_array_int = list_array.astype(int) #transform values into integer values
    coord_list_round.append(list_array_int) #saves arrays in list


#x_max - x_min of common extent in dem
width = np.asscalar(np.int16(coord_list_round[2][0][0]-coord_list_round[0][0][0])) #befor calculation it transforms numpy dtype into native python dtype
#y_min - y_max of common extent in dem
height = np.asscalar(np.int16(coord_list_round[1][0][1]-coord_list_round[0][0][1])) #befor calculation it transforms numpy dtype into native python dtype

# iterates through each raster in the raster list
arr_list = []
for i in range(len(raster_list)):
    rb = raster_list[i].GetRasterBand(1) #loads first band
    xoff = np.asscalar(np.int16(coord_list_round[0][i][0])) #determines raster specific x offset
    yoff = np.asscalar(np.int16(coord_list_round[0][i][1])) #determines raster specific y offset
    arr = rb.ReadAsArray(xoff, yoff, width, height) # slices array of the common extent of all rasters out
    print("Shape of array:", arr.shape)
    arr_list.append(arr) # saves array into list

# Calculate Summary Statistics (Mean, Min, Max) for elevation and SLOPE
arr_dem_m = np.ma.masked_array(arr_list[0], arr_list[0] == 65536) #creates a masked array
arr_slope_m = np.ma.masked_array(arr_list[1], arr_list[1] <= 0) # creates a masked array
print("Mean of DEM:", arr_dem_m.mean())
print("Min of DEM:", arr_dem_m.min())
print("Max of DEM:", arr_dem_m.max())
print("Mean of Slope:", arr_slope_m.mean())
print("Min of Slope:", arr_slope_m.min())
print("Max of Slope:", arr_slope_m.max())

# EXERCISE 1.2: Create Mask and write raster out

mask_dem = np.zeros((1240, 599), dtype=np.int16)
mask_slope = np.zeros((1240, 599), dtype=np.int16)
mask_slope[arr_slope_m < 30] = 1
mask_dem[arr_dem_m < 1000] = 1
mask_final = mask_slope * mask_dem


dtype = rb.DataType
pr = raster_list[0].GetProjection()
gt_mask = raster_list[0].GetGeoTransform()


# Write mask out
# ATTENTION the origin of the mask is not yet right
outfile = wd+"mask.tif"
drvR = gdal.GetDriverByName('GTiff')
outDS = drvR.Create(outfile, 599, 1240, 1, dtype)
outDS.SetProjection(pr)
outDS.SetGeoTransform(gt_mask)
outDS.GetRasterBand(1).WriteArray(mask_final, 0, 0)
outDS = None

# EXERCISE 1.3: Calculate proportional areas
area_total = 277.73114823372805*599*1240*277.7311482337280
area_mask = mask_final.sum()*277.7311482337280*277.7311482337280
area_prop = area_mask/area_total*100
print("Proportion of masked area: ", round(area_prop,2), "%")

# EXERCISE 2.1:
thp_mask = np.zeros((1240, 599), dtype=np.int16)
thp_mask[arr_list[2] == 2003] = 1
dem_2003 = thp_mask * arr_list[0]
dem_2003_m = np.ma.masked_array(dem_2003, dem_2003 == 0)
print("Masked: ",dem_2003_m.mean())

#possibility 1: fill array with one loop, # no column names in csv file
arr_out = np.zeros((19,3), dtype=np.float)
for i in range(0,19):
    thp_mask = np.zeros((1240, 599), dtype=np.int16)
    thp_mask[arr_list[2] == i + 1997] = 1
    arr_dem = thp_mask * arr_dem_m
    arr_dem_m2 = np.ma.masked_array(arr_dem, arr_dem == 0)
    arr_slope = thp_mask * arr_slope_m
    arr_slope_m2 = np.ma.masked_array(arr_slope, arr_slope == 0)
    arr_out[i, 0] = i + 1997
    arr_out[i, 1] = arr_dem_m2.mean()
    arr_out[i, 2] = arr_slope_m2.mean()
np.savetxt(r'O:\Student_Data\CJaenicke\04_SoSe_18\GeoPython\data\Assignment03\stat_per_years.csv', arr_out, delimiter=",", fmt='%1.2f', header='Year, Mean_elev, Mean_slope')

#possibility 2: write list with triples # error in output
list_out = [('Year','Mean_elev','Mean_slope')]
for i in range(0,19):
    thp_mask = np.zeros((1240, 599), dtype=np.int16)
    thp_mask[arr_list[2] == i + 1997] = 1
    arr_dem = thp_mask * arr_dem_m
    arr_dem_m2 = np.ma.masked_array(arr_dem, arr_dem == 0)
    arr_slope = thp_mask * arr_slope_m
    arr_slope_m2 = np.ma.masked_array(arr_slope, arr_slope == 0)
    list_out.append((i+1997,arr_dem_m2.mean(), arr_slope_m2.mean()))
print(list_out)

#ATTENTION output file contains brackets
outputFile = open(r'O:\Student_Data\CJaenicke\04_SoSe_18\GeoPython\data\Assignment03\statistics_per_year.txt', 'w')
for item in list_out:
    outputFile.write(str(item))
    outputFile.write('\n')

#possibility 3: fill array with two loops
#ATTENTION doesn't work yet
arr_m_list = [arr_dem_m, arr_slope_m]
arr_out2 = np.zeros((19,3), dtype=np.float)
thp_mask2 = np.zeros((1240, 599), dtype=np.int16)
for i in range(0, 19):
    arr_out2[i,0] = i + 1997
    thp_mask2[arr_list[2] == i + 1997] = 1
    for j in range(0,1):
        arr_i = thp_mask2 * arr_m_list[j]
        arr_i_m = np.ma.masked_array(arr_i, arr_i == 0)
        arr_out2[i,j+1] = arr_i_m.mean() #here is the mistake, I can't get my head around

# #### END TIME-COUNT AND PRINT TIME STATS #### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")