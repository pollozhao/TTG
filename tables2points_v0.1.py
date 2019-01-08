# tables2points.py MakeXYLayer
# Description: Creates an XY layer and exports it to a layer file

import arcpy, os, time
from arcpy import env

start_t = time.time()

# Set environment settings
env.workspace = "C:/Zhao/job/14022_SNCF/route_data/DonneesGPS_LGV_Sud_Est_Trace_OK"
csvFolder = env.workspace + "/csv/"
ws = env.workspace

filelist = os.listdir(csvFolder)

for currentfile in filelist:
    print(currentfile)
    # Set the local variables
    in_Table = csvFolder + currentfile
    x_coords = "Field1"
    y_coords = "Field2"
    #z_coords = "POINT_Z"
    out_Layer = currentfile.replace(".CSV","")
    out_shp = "/shp/" + currentfile.replace(".CSV",".shp")

    # Make the XY event layer...
    arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, "WGS 1984", "")

    # Now convert to a feature class
    arcpy.FeatureClassToFeatureClass_conversion (out_Layer, ws, out_shp)

end_t = time.time()
print('Completed computing in: ', round(end_t-start_t, 2),'s')
