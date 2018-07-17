
# ############################################################################################################# #
# Raw-example for a basic script to be executed in python. The format is only a recommendation and everyone is
# encouraged to modify the scripts to her/his own needs.
# (c) Thilo Wellmann, Humboldt-Universität zu Berlin, 4/23/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import os
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
#from osgeo import osr
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
#ROOT_FOLDER = "O:/Student_Data/thomsens/MSc_SS4/python/session_7/Assignment06_data/"
ROOT_FOLDER = "D:/DATA_THILO/Python/Assignment06/Data/"
numbers_reclass = (4,6,7,8,9,10,12,14,15,16,20,21,22,23)
# ####################################### Functions ########################################################## #
def LOAD_RASTERS(root_folder):
    rasternames = os.listdir(root_folder)
    rasters = []
    arrays =[]
    for rastername in rasternames:
        rasters.append(gdal.Open(root_folder + rastername))

        ds = (gdal.Open(root_folder + rastername))
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        arrays.append(np.array(ds.GetRasterBand(1).ReadAsArray(0,0,cols,rows))) # (originx, originy, sliceSizex, slicesize y)


    return rasters, arrays, rasternames


def PlotArray2d(array):
    fig = plt.figure(figsize=(6, 3.2))

    ax = fig.add_subplot(111)
    ax.set_title('colorMap')
    plt.imshow(array)
    ax.set_aspect('equal')

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    plt.show()



def EXPORTARRAYTODISK(raster, arrayToExport, rastername ):
    os.chdir("D:/DATA_THILO/Python/Assignment03/Data/Export/")
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    nr_bands = 1
    #srs = osr.SpatialReference()
    #srs.ImportFromEPSG(26741)
    #proj = osr.SpatialReference(wkt=raster.GetProjection())
    SrsProjection = raster.GetProjection()
    #srs=osr.SpatialReference(wkt=SrsProjection)
    #srs.GetAttrValue('geogcs')
    GeoTransform = raster.GetGeoTransform()
    GeoTransform_list =  list(GeoTransform)
    GeoTransform_list[0] = 1399618.9
    GeoTransform_list[3] = 705060.6
    driver = gdal.GetDriverByName("GTiff")

    dataset_out = driver.Create(rastername, cols, rows, nr_bands, gdal.GDT_Float64  )
    dataset_out.SetGeoTransform(GeoTransform_list)
    dataset_out.SetProjection(SrsProjection)
    out_band = dataset_out.GetRasterBand(1)
    out_band.WriteArray(arrayToExport)

    # actually write to disk
    dataset_out.FlushCache()
    dataset_out = None
    driver = None

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


def sdi(data):
    """ Given a hash { 'species': count } , returns the SDI

    >>> sdi({'a': 10, 'b': 20, 'c': 30,})
    1.0114042647073518"""

    from math import log as ln

    def p(n, N):
        """ Relative abundance """
        if n is  0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)

    N = np.sum(data)

    return -np.sum(p(n, N) for n in data if n is not 0)

def calc_sdi(data_array):
    array_values,array_count = np.unique(data_array, return_counts=True)
    sdi_array = sdi(array_count)

    return sdi_array


def make_raster(in_ds, fn, data, data_type, nodata=None):
    """Create a one-band GeoTIFF.
    in_ds     - datasource to copy projection and geotransform from
    fn        - path to the file to create
    data      - NumPy array containing data to write
    data_type - output data type
    nodata    - optional NoData value
    """
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(
        fn, in_ds.RasterXSize, in_ds.RasterYSize, 1, data_type)
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    if nodata is not None:
        out_band.SetNoDataValue(nodata)
    out_band.WriteArray(data)
    out_band.FlushCache()
    out_band.ComputeStatistics(False)
    return out_ds




rasters, arrays, rasternames = LOAD_RASTERS(ROOT_FOLDER)
win_size_m = [150,300,450]

for rasname in rasternames:
    ras = gdal.Open(ROOT_FOLDER + rasname)
    ds = gdal.Open(ROOT_FOLDER + rasname)
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    arr = np.array(ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows))
    for number_reclass in numbers_reclass:
        arr[arr == number_reclass] = 1
    res = ras.GetGeoTransform()[1]
    rassubstr = rasname.split(".")[0]
    for window in win_size_m:
        pix_offset = int(window/res)
        win_size = int(1+(2*pix_offset))
        slices = make_slices(arr,(win_size,win_size))
        slices_stack = np.ma.dstack(slices)
        out_arr = np.ones((rows,cols)) * -99
        out_arr[pix_offset:-pix_offset, pix_offset:-pix_offset] = np.apply_along_axis(calc_sdi, 2, slices_stack)
        out_name = ROOT_FOLDER + rassubstr + "_" + str(window) + ".tif"
        make_raster(ds,out_name,out_arr,gdal.GDT_Float64, -99)
        print("Raster: " + out_name + " successfully created.")

    del ds

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")


