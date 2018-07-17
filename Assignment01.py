# Clemens Jänicke, Humboldt-Universität zu Berlin

# #### LOAD REQUIRED LIBRARIES ####
import time
import os
import glob

# #### SET TIME-COUNT ####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

# #### FOLDER PATHS & global variables ####
wd = r'O:\Student_Data\CJaenicke\04_SoSe_18\GeoPython\data\Assignment01_data\Part01_Landsat'
wd2 = r'O:\Student_Data\CJaenicke\04_SoSe_18\GeoPython\data\Assignment01_data\Part02_GIS-Files'

# #### PROCESSING ####
footprintList = os.listdir(wd)

# Sanity Check 1)
for footprint in footprintList:
    wd_new = wd + '\\' + footprint
    list = os.listdir(wd_new)

    length = len(list)
    print('footprint: ' + footprint + '; number of scenes: ' + str(length))

    i_08 = 0
    i_07 = 0
    i_05 = 0
    i_04 = 0
    for scene in list:
        if scene[:4] == 'LC08':
            i_08 = i_08 + 1
        elif scene[:4] == 'LE07':
            i_07 = i_07 + 1
        elif scene[:4] == 'LT05':
            i_05 = i_05 + 1
        elif scene[:4] == 'LT04':
            i_04 = i_04 + 1
        else:
            print('moet')
            #pass

    print('LC08: ' + str(i_08))
    print('LE07: ' + str(i_07))
    print('LT05: ' + str(i_05))
    print('LT04: ' + str(i_04))
    print('countercheck number of scenes:' + str(i_08 + i_07 + i_05 + i_04))

# Sanity Check 2)
erroneous_file_list = []
for footprint in footprintList:
    wd_footprint = wd + '\\' + footprint
    scene_list = os.listdir(wd_footprint)
    for scene in scene_list:
        wd_scene = wd_footprint + '\\' + scene
        file_list = os.listdir(wd_scene)
        if scene[:4] == 'LC08' or scene[:4] == 'LE07':
            if len(file_list) == 19:
                pass
            else:
                erroneous_file_list.append(wd_scene)
        elif scene[:4] == 'LT05' or scene[:4] == 'LT04':
            if len(file_list) == 21:
                pass
            else:
                erroneous_file_list.append(wd_scene)
outputFile = open(r'O:\Student_Data\CJaenicke\04_SoSe_18\GeoPython\data\Assignment01_data\erroneous_scenes.txt', 'w')
for item in erroneous_file_list:
    outputFile.write('%s\n' % item)

# Exercise II 1)
# solution 1
GISfileList = os.listdir(wd2)
SHPcounter = len(glob.glob1(wd2,'*.shp'))
print('number of shapefiles: ' + str(SHPcounter))
TIFcounter = len(glob.glob1(wd2,'*.tif'))
print('number of raster files: ' + str(TIFcounter))

# Exercise II 2)
missingFilesList = []
for file in GISfileList:
    if file.endswith('.shp'):
        filename = file.split('.')[0]
        dbfName = filename + '.dbf'
        prjName = filename + '.prj'
        #cpgName = filename + '.cpg'
        #sbnName = filename + '.sbn'
        #sbxName = filename + '.sbx'
        shxName = filename + '.shx'
        if dbfName in GISfileList:
            pass
        else:
            missingFilesList.append(dbfName)
        if prjName in GISfileList:
            pass
        else:
            missingFilesList.append(prjName)
        #if cpgName in GISfileList:
        #    pass
        #else:
        #    missingFilesList.append(cpgName)
        #if sbnName in GISfileList:
        #    pass
        #else:
        #    missingFilesList.append(sbnName)
        #if sbxName in GISfileList:
        #    pass
        #else:
        #    missingFilesList.append(sbxName)

    else:
        pass
outputMissingFiles = open(r'O:\Student_Data\CJaenicke\04_SoSe_18\GeoPython\data\Assignment01_data\missing_files.txt', 'w')
for item in missingFilesList:
    outputMissingFiles.write('%s\n' % item)


# #### END TIME-COUNT AND PRINT TIME STATS ####
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")