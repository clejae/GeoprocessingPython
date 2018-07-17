import time
from osgeo import ogr
import pandas as pd

# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

# lycoun = '/home/florian/Geodata_with_Python/session5/Assignment04_data/gadm36_dissolve.shp'
# lypa   = '/home/florian/Geodata_with_Python/session5/Assignment04_data/WDPA_May2018-shapefile-polygons.shp'
#
# country = ogr.Open(lycoun)
# pas     = ogr.Open(lypa)
#
# cl = country.GetLayer()
# pl = pas.GetLayer()
# pl.SetAttributeFilter("MARINE='0'" and ("STATUS = 'Designated'" or "STATUS = 'Established'"))
#
# k = ['Country ID', 'Country Name', 'PA Category', 'PA Name', 'PA Area', 'PA Established']
# v = [[], [], [], [], [], []]
# r = dict(zip(k, v))
#
# for feat in cl:
#     extr = feat.geometry().Clone()
#     pl.SetSpatialFilter(extr)
#     print(feat.GetField('Name_0'))
#
#     for sub in pl:
#         r['Country ID'].append(feat.GetField('ID_0'))
#         r['Country Name'].append(feat.GetField('NAME_0'))
#         r['PA Category'].append(sub.GetField('IUCN_CAT'))
#         r['PA Name'].append(sub.GetField('NAME'))
#         r['PA Area'].append(sub.GetField('GIS_AREA'))
#         r['PA Established'].append(sub.GetField('STATUS_YR'))
#
#     pl.SetSpatialFilter(None)
#
# cl.ResetReading() # sets country's starting feature to zero
#
# # store the extracts
# df = pd.DataFrame(data=r)
# df.to_csv('/home/florian/Geodata_with_Python/session5/inter_GIS_AREA.csv', sep=',',index=False)

# load the extracts
da = pd.read_csv('/home/florian/Geodata_with_Python/session5/inter_GIS_AREA.csv', sep=',', lineterminator='\n')

kill = ['Not Reported', 'Not Applicable', 'Not Assigned']

da = da[~da['PA Category'].isin(kill)]
da2 = da.groupby(['Country ID', 'Country Name', 'PA Category'])['PA Area'].count()
da3 = da.groupby(['Country ID', 'Country Name', 'PA Category'])['PA Area'].mean()
da4 = da.groupby(['Country ID', 'Country Name', 'PA Category'])['PA Area'].max()
da['test'] = da.groupby(['Country ID', 'Country Name', 'PA Category'])['PA Area'].transform(max) == da['PA Area']
da5 = da.groupby(['Country ID', 'Country Name', 'PA Category', 'test'])['PA Name'].unique()
da6 = da.groupby(['Country ID', 'Country Name', 'PA Category', 'test'])['PA Established'].unique()

da5df = pd.DataFrame(da5).reset_index()
da5df.columns = ['ID', 'Country', 'Cat', 'test', 'Name']
da5df = da5df[da5df['test'] == True]
da5df = pd.DataFrame(da5df).reset_index()
da5   = da5df['Name'].str[0]

da6df = pd.DataFrame(da6).reset_index()
da6df.columns = ['ID', 'Country', 'Cat', 'test', 'Estab']
da6df = da6df[da6df['test'] == True]
da6df = pd.DataFrame(da6df).reset_index()
da6 = da6df['Estab'].str[0]
da6 = da6.astype(int)

res = pd.DataFrame(da2).reset_index()
res.columns = ['Country ID', 'Country Name', 'PA Category', '# PAs']
res['Mean area of PAs']              = da3.values
res['Area of largest PA']            = da4.values
res['Name of largest PA']            = da5.values
res['Year of establ. Of largest PA'] = da6.values

r1 = da.groupby(['Country ID', 'Country Name'])['PA Area'].count()
r2 = da.groupby(['Country ID', 'Country Name'])['PA Area'].mean()
r3 = da.groupby(['Country ID', 'Country Name'])['PA Area'].max()
da['test'] = da.groupby(['Country ID', 'Country Name'])['PA Area'].transform(max) == da['PA Area']
r4 = da.groupby(['Country ID', 'Country Name', 'PA Category', 'test'])['PA Name'].unique()
r5 = da.groupby(['Country ID', 'Country Name', 'PA Category', 'test'])['PA Established'].unique()

r4df = pd.DataFrame(r4).reset_index()
r4df.columns = ['ID', 'Country', 'Cat', 'test', 'Name']
r4df = r4df[r4df['test'] == True]
r4df = pd.DataFrame(r4df).reset_index()
r4   = r4df['Name'].str[0]

r5df = pd.DataFrame(r5).reset_index()
r5df.columns = ['ID', 'Country', 'Cat', 'test', 'Estab']
r5df = r5df[r5df['test'] == True]
r5df = pd.DataFrame(r5df).reset_index()
r5 = r5df['Estab'].str[0]
r5 = r5.astype(int)

res2 = pd.DataFrame(r1).reset_index()
res2.columns = ['Country ID', 'Country Name', '# PAs']
res2['Mean area of PAs']              = r2.values
res2['Area of largest PA']            = r3.values
res2['Name of largest PA']            = r4.values
res2['Year of establ. Of largest PA'] = r5.values
res2['PA Category'] = 'ALL'
res2 = res2[['Country ID', 'Country Name', 'PA Category', '# PAs',
             'Mean area of PAs', 'Area of largest PA', 'Name of largest PA', 'Year of establ. Of largest PA']]

res3 = pd.concat([res, res2], ignore_index=True)
sorti = ['ALL', 'Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI']
res3['PA Category'] = res3['PA Category'].astype('category')
res3['PA Category'].cat.set_categories(sorti, inplace=True)

res3 = res3.sort_values(by=['Country ID', 'PA Category'])
res3['Mean area of PAs'] = round(res3['Mean area of PAs'], 2)
res3['Area of largest PA'] = round(res3['Area of largest PA'], 2)
res3.to_csv('/home/florian/Geodata_with_Python/session5/Britta_Clemens_Flo_Julia_Assign4.csv', sep=',',index=False)


# #### END TIME-COUNT AND PRINT TIME STATS #### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")