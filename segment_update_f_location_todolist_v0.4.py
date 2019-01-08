segmentsFolder = "C:/Zhao/job/QVCS/Sites/UK/Chiltern/Data/Segments"
outputFile = "all_ST.txt"
findoutF = "ST"
findoutAG = "xa"

import os, time

start_t = time.time()

segmentListAll = os.listdir(segmentsFolder)
##segmentListAll = [
##'ECM9~Waverley_East_End~Edinburgh_Waverley_Station.seg',
##'EGM4~Edinburgh_Waverley_Station~Waverley_West_End.seg',
##'EGM3~Waverley_West_End~Haymarket.seg',
##'EGM2~Haymarket~Haymarket_East_Jn.seg',
##'EGM2~Haymarket_East_Jn~Haymarket_Central_Jn.seg',
##'EGM2~Haymarket_Central_Jn~Haymarket_West_Jn.seg',
##]

print("total segments: ", len(segmentListAll))

ag_list_seg, ag_list_km, ag_list_name = [],[],[]
F_list_seg, F_list_km, F_list_name = [],[],[]

for seg in segmentListAll:

    current_segment = segmentsFolder + "/" + seg
    print (current_segment)
    fin = open(current_segment)

    for line in fin:
        if line[:1].isdigit() or line[:1] == "#":
            route_t = line.split('\t')

            if route_t[1] == findoutAG:
                ag_list_seg.append(seg)
                ag_list_km.append(route_t[0])
                ag_list_name.append(route_t[2].replace('"',''))
            
            elif route_t[1] == "f" and route_t[3] == findoutF:
                F_list_seg.append(seg)
                F_list_km.append(route_t[0])
                if len(route_t) == 4:
                    F_list_name.append("_blank_")
                elif len(route_t) == 5:
                    F_list_name.append(route_t[4].replace('\n',''))
                else:
                    F_list_name.append(''.join(route_t[4]))

    fin.close()

fout = open(outputFile, "w")

print(len(F_list_km), len(F_list_km))
print(len(ag_list_km), len(ag_list_km))

##for i in range(len(ag_list_km)):
##    fout.write(ag_list_seg[i]+','+ag_list_km[i]+','+ag_list_name[i]+'\n')

for j in range(len(F_list_km)):
    fout.write(F_list_seg[j]+','+F_list_km[j]+','+ findoutF +','+F_list_name[j]+'\n')

fout.close()

end_t = time.time()
print('Completed computing in: ', round(end_t-start_t, 2),'s')
