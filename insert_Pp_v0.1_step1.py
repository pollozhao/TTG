import os, time, math, numpy, scipy
from scipy import spatial

start = time.time()

segmentsFolder = "C:/Zhao/job/QVCS/Sites/UK/ScotRail/Data/Segments"

todo_list = "platform_input.csv"

toinsert_list = "platform_to_insert.csv"

##seg_file = "HMN1~Motherwell_Jn~HMN1-HMN2.seg"
##station_pt = [(55.78151667,-3.995144444),(55.78268056,-3.994286111)]



def kd_tree(point_array, find_list):
    mytree = scipy.spatial.cKDTree(point_array)
    dist, indexes = mytree.query(find_list)
    return indexes



def lat_long_distance(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    radius = 6371 # km
 
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
 
    return d



def Pp_distance_float(current_point, closest_point, previous_point):
    if lat_long_distance(current_point,previous_point) < lat_long_distance(previous_point,closest_point):
        p_distance_closest = 0 - lat_long_distance(current_point,closest_point)
    else:
        p_distance_closest = lat_long_distance(current_point,closest_point)
  
    return p_distance_closest



def calculate_platform_boundary(f_segment,f_station_pt):

    seg_km, seg_pt = [],[]
    fin = open(f_segment)

    for line in fin:
        if line[:1].isdigit() or line[:1] == "#":
            current_line = line.split()

            if current_line[1] == "g":
                seg_km.append(current_line[0])
                seg_pt.append((current_line[2],current_line[3]))
    fin.close()

    result = kd_tree(seg_pt,f_station_pt)

    Pp0 = Pp_distance_float(f_station_pt[0], (float(seg_pt[int(result[0])][0]),float(seg_pt[int(result[0])][1])), (float(seg_pt[int(result[0])-1][0]),float(seg_pt[int(result[0])-1][1])))
    Pp1 = Pp_distance_float(f_station_pt[1], (float(seg_pt[int(result[1])][0]),float(seg_pt[int(result[1])][1])), (float(seg_pt[int(result[1])-1][0]),float(seg_pt[int(result[1])-1][1])))

#    print(Pp0,Pp1)
        
    if (float(seg_km[int(result[0])]) + Pp0) < (float(seg_km[int(result[1])] )+ Pp1):
        return float(seg_km[int(result[0])]) + Pp0, float(seg_km[int(result[1])] )+ Pp1
    else:
        return float(seg_km[int(result[1])]) + Pp1, float(seg_km[int(result[0])] )+ Pp0





segment_array, station_array, pfs_lat, pfs_lon, pfe_lat, pfe_lon = [],[],[],[],[],[]

fin = open(todo_list)
fout = open(toinsert_list,"w")
for line in fin:
    lineT = line.split(',')
    segment_array.append(lineT[0])
    station_array.append(lineT[1])
    pfs_lat.append(lineT[2])
    pfs_lon.append(lineT[3])
    pfe_lat.append(lineT[4])
    pfe_lon.append(lineT[5])

    print(segmentsFolder+"/"+lineT[0])
    P, p = calculate_platform_boundary(segmentsFolder+"/"+lineT[0],[(float(lineT[2]),float(lineT[3])),(float(lineT[4]),float(lineT[5]))])
    print(P,p)

    insert_str_P = str(round(P,3)) + "\tf\t0\tP\t" + lineT[1] + "\n"
    insert_str_p = str(round(p,3)) + "\tf\t0\tp\t" + lineT[1] + "\n"
    print (insert_str_P)
    print (insert_str_p)
    fout.write(segmentsFolder+"/"+lineT[0] + "," + str(round(P,3)) + " P," + str(round(p,3)) + " p,"+ lineT[1] + "\n")
    
fin.close()
fout.close()

total_action = len(station_array)

end = time.time()
print('Completed computing in: ', round(end-start, 2),'s')
