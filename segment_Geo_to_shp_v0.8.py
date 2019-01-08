import arcpy
from arcpy import env
import os, time


start_t = time.time()
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984')

segmentsFolder = 'A:/Zhao/job/14001_Hitachi_LNER/Segments20181031'

env.workspace = segmentsFolder
csvFolder = env.workspace + '/csv/'
ws = env.workspace


def format_name(input_str):
    fn = input_str.replace('-','_').replace('~','_').replace('(','_').replace(')','_').replace('&','_').replace("'","")
    return fn


ListAll = os.listdir(segmentsFolder)

segmentListAll = []
for files in ListAll:
    if files.endswith('.seg'):
        segmentListAll.append(files)
        
##segmentListAll = [
##'ANI1~ECN5-ANI1~Kittybrewster_Jn.seg',
##]

print('total segments: ' + str(len(segmentListAll)))


try:
    os.stat(segmentsFolder + '/csv')
except:
    os.mkdir(segmentsFolder + '/csv')

try:
    os.stat(segmentsFolder + '/shp')
except:
    os.mkdir(segmentsFolder + '/shp')

try:
    os.stat(segmentsFolder + '/shp/point')
except:
    os.mkdir(segmentsFolder + '/shp/point')

try:
    os.stat(segmentsFolder + '/shp/line')
except:
    os.mkdir(segmentsFolder + '/shp/line')
    

for seg in segmentListAll:
    
    current_segment = segmentsFolder + '/' + seg

    output_csv = segmentsFolder + '/csv/' + format_name(seg).replace('.seg','.csv')

    print (current_segment)

    fout = open(output_csv, 'w')
    fout_table = open(output_csv.replace('.csv','_table.csv'), 'w')
    
    fin = open(current_segment)

    for line in fin:
        if line[:1].isdigit(): #or line[:1] == "#":
            route_t = line.strip().split('\t')
            if route_t[1] == 'g':
                fout.write(route_t[2] + ',' + route_t[3] + '\n')
                
            elif route_t[1] != 'c':
                fout_table.write(route_t[0] + ',' + route_t[1] + ',' + ','.join(route_t[2:len(route_t)]) + '\n')

               
    fout.close()
    fout_table.close()

    in_Table = output_csv
    x_coords = "Field2"
    y_coords = "Field1"
#    z_coords = "Field4"

    out_Layer = format_name(seg).replace('.seg','')
    out_shp = '/shp/point/' + format_name(seg).replace('.seg','.shp')

    arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, 'WGS 1984', '')
    if arcpy.Exists(out_shp):
        arcpy.Delete_management(out_shp)
    arcpy.FeatureClassToFeatureClass_conversion (out_Layer, ws, out_shp)

    out_shp_line = segmentsFolder + '/shp/line/' + format_name(seg).replace('.seg','.shp')
    if arcpy.Exists(out_shp_line):
        arcpy.Delete_management(out_shp_line)
    arcpy.PointsToLine_management(out_shp, out_shp_line)
    
    arcpy.AddField_management (out_shp_line, 'Segment', 'text', '', '', '100')
    arcpy.CalculateField_management (out_shp_line, 'Segment', '"' + seg.replace('.seg','') + '"', 'PYTHON')

    arcpy.AddField_management (out_shp_line, 'ELR', 'text', '', '', '10')
    arcpy.CalculateField_management (out_shp_line, 'ELR', '"' + seg.split('~')[0] + '"', 'PYTHON')
    
    seglenghlines = open(current_segment, 'r').readlines()
    seglengh = float(seglenghlines[1].split()[1])

    for l1 in seglenghlines:
        lt1 = l1.split('\t')
        if len(lt1) > 3 and (lt1[3] == 'm' or lt1[3] == 'k'):
            segstartpost = float(lt1[4])
            break
        
    for l3 in seglenghlines:
        lt3 = l3.split('\t')
        if len(lt3) > 8 and lt3[3] == 'cl':
            segsline = lt3[4]
            segslinecode = lt3[5]
            segslor = lt3[6]
            segsdir = lt3[7]
            break
        
    for l2 in reversed(seglenghlines):
        lt2 = l2.split('\t')
        if len(lt2) > 3 and (lt2[3] == 'm' or lt2[3] == 'k'):
            segendpost = float(lt2[4])
            break

    arcpy.AddField_management (out_shp_line, 'Length', 'float', '', '', '')
    arcpy.CalculateField_management (out_shp_line, "Length", seglengh, 'PYTHON')

    arcpy.AddField_management (out_shp_line, 'StartPost', 'float', '', '', '')
    arcpy.CalculateField_management (out_shp_line, "StartPost", segstartpost, 'PYTHON')
    
    arcpy.AddField_management (out_shp_line, 'EndPost', 'float', '', '', '')
    arcpy.CalculateField_management (out_shp_line, "EndPost", segendpost, 'PYTHON')

    arcpy.AddField_management (out_shp_line, 'Track', 'text', '', '', '50')
    arcpy.CalculateField_management (out_shp_line, 'Track', '"' + segsline + '"', 'PYTHON')
    arcpy.AddField_management (out_shp_line, 'TrackCode', 'text', '', '', '10')
    arcpy.CalculateField_management (out_shp_line, 'TrackCode', '"' + segslinecode + '"', 'PYTHON')
    arcpy.AddField_management (out_shp_line, 'LOR', 'text', '', '', '10')
    arcpy.CalculateField_management (out_shp_line, 'LOR', '"' + segslor + '"', 'PYTHON')
    arcpy.AddField_management (out_shp_line, 'Direction', 'text', '', '', '1')
    arcpy.CalculateField_management (out_shp_line, 'Direction', '"' + segsdir + '"', 'PYTHON')
    
end_t = time.time()
print('Completed computing in: ' + str(round(end_t-start_t, 2)) + 's')
