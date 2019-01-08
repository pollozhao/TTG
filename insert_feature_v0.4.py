import os, time, math, numpy, scipy, shutil
from scipy import spatial
import numpy as np

start = time.time()

segmentsFolder = "C:/Jobs/ATW/tunnel/Segments_addtunnel_14102014/"
tiploc_list = "tunnel.csv"
paired_feature = "T"

#tiploc_list format:
#ELR,decimal_mileage,name,code,STANOX

#feature_list format:
#ELR,decimal_mileage,name,t_type



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




def calculatSegDistance(dis1,mp1,dis2,mp2,calmp):
#    print(dis1,mp1)
#    print(round((dis2-(mp2-calmp)*(dis2-dis1)/(mp2-mp1)),3),calmp)
#    print(dis2,mp2)
    return round((dis2-(mp2-calmp)*(dis2-dis1)/(mp2-mp1)),3)
    


def locateSegment(elr, milepost, segment_file):
    
    F_list_km,F_list_name = [],[]
    
    fin = open(segmentsFolder + segment_file)

    for line in fin:
        if line[:1].isdigit() or line[:1] == "#":
            route_t = line.split()
            if route_t[1] == "f" and route_t[3] == "m":
                F_list_km.append(float(route_t[0].replace('#','')))
                F_list_name.append(float(route_t[4]))
		
    if elr == segment_file.split("~")[0]:

        if F_list_name[0] < F_list_name[-1]:
            increaseMP = True
            if F_list_name[0] <= float(milepost) and float(milepost) < F_list_name[-1]:
#                print(F_list_name[0],float(milepost),F_list_name[-1],segment_file)
                closest = min(F_list_name, key=lambda x:abs(x-float(milepost)))

                if float(milepost) < closest:
                    seg_dis = calculatSegDistance(F_list_km[F_list_name.index(closest)],closest,F_list_km[F_list_name.index(closest)-1],F_list_name[F_list_name.index(closest)-1],float(milepost))
                elif float(milepost) < closest:
                    seg_dis = closest
                else:
                    seg_dis = calculatSegDistance(F_list_km[F_list_name.index(closest)],closest,F_list_km[F_list_name.index(closest)+1],F_list_name[F_list_name.index(closest)+1],float(milepost))
                return seg_dis
            else:
                return None
        else:
            increaseMP = False
            if F_list_name[0] >= float(milepost) and float(milepost) > F_list_name[-1]:
#                print(F_list_name[0],float(milepost),F_list_name[-1],segment_file)
                closest = min(F_list_name, key=lambda x:abs(x-float(milepost)))
                if float(milepost) < closest:
                    seg_dis = calculatSegDistance(F_list_km[F_list_name.index(closest)],closest,F_list_km[F_list_name.index(closest)+1],F_list_name[F_list_name.index(closest)+1],float(milepost))
                elif float(milepost) < closest:
                    seg_dis = closest
                else:
                    seg_dis = calculatSegDistance(F_list_km[F_list_name.index(closest)],closest,F_list_km[F_list_name.index(closest)-1],F_list_name[F_list_name.index(closest)-1],float(milepost))            
                return seg_dis
            else:
                return None



def insert2segment(locateResult,tiploc_name,tiploc_code,seg,fea_type):
    f_fin = open(segmentsFolder + seg)
    f_fout = open(segmentsFolder + seg + ".temp", "w")
    todo = 1
    for f_line in f_fin:
        if f_line[:1].isdigit() or line[:1] == "#":
            f_lineT = f_line.split()
            if float(f_lineT[0]) >= float(locateResult):
                if todo:
#                    f_fout.write(str(locateResult) + "\tf\t0\tST\t" + str(tiploc_name) + "\t" + tiploc_code)
                    f_fout.write(str(locateResult) + "\tf\t0\t" + fea_type + "\t" + str(tiploc_name) + "\n")
                    todo = 0
                    f_fout.write(f_line)
                else:
                    f_fout.write(f_line)
            else:
               f_fout.write(f_line)                                
        else:
            f_fout.write(f_line)
            
    f_fin.close()
    f_fout.close()
    shutil.move((segmentsFolder + seg + ".temp"), segmentsFolder + seg)




def insertTIPLOC(tiploc_elr, tiploc_mc, tiploc_name, tiploc_code, segment_list, fea_type):
    for seg in segment_list:
        locateResult = locateSegment(tiploc_elr, tiploc_mc, seg)
#        print(locateResult,tiploc_name,seg)
        if locateResult != None:
            print(tiploc_name.replace('\n','\t'),locateResult,"\t",seg)
            insert2segment(locateResult,tiploc_name,tiploc_code,seg,fea_type)


            
def pairFeature(seg, paired_feature):
    f_fin = open(segmentsFolder + seg)
    f_fout = open(segmentsFolder + seg + ".temp", "w")
    topair = 0
    for f_line in f_fin:
        if f_line[:1].isdigit() or line[:1] == "#":
            f_lineT = f_line.split()
            if f_lineT[3] == paired_feature and topair == 0:
                topair == 1
                f_fout.write(f_line)
            elif f_lineT[3] == paired_feature and topair == 1:
                f_fout.write(f_lineT[0] + "\tf\t0\t" + paired_feature.lower() + "\t" + f_lineT[4] + "\n")
                topair == 0
            else:
                f_fout.write(f_line)
        else:
            f_fout.write(f_line)
            
    f_fin.close()
    f_fout.close()
    shutil.move((segmentsFolder + seg + ".temp"), segmentsFolder + seg)





tiploc_elr, tiploc_mc, tiploc_name, tiploc_code, tiploc_stanox = [],[],[],[],[]
tiploc_segment, tiploc_distance= [],[]
fea_type = []

segment_folder_list = os.listdir(segmentsFolder)
##segment_folder_list = [
##'AYR6~Falkland_Junction~Lochgreen_Junction.seg',
##'AYR6~Falkland_Junction~Newton_Junction.seg',
##'AYR6~Lochgreen_Junction~Falkland_Junction.seg',
##'AYR6~Newton_Junction~Falkland_Junction.seg'
##]



fin = open(tiploc_list)

for line in fin:
    lineT = line.split(',')
    tiploc_elr.append(lineT[0])
    tiploc_mc.append(lineT[1])
    tiploc_name.append(lineT[2])
#    tiploc_code.append(lineT[3])
#    tiploc_stanox.append(lineT[4])
    fea_type.append(lineT[3].replace('\n',''))

    insertTIPLOC(lineT[0],lineT[1],lineT[2],"code",segment_folder_list,lineT[3].replace('\n',''))

#    print(lineT[0]+"_"+lineT[1]+"_"+lineT[2]+"_"+lineT[3]+t_l_s+t_l_d)
fin.close()

for seg in segment_folder_list:
    pairFeature(seg, paired_feature)

end = time.time()
print('Completed computing in: ', round(end-start, 2),'s')
