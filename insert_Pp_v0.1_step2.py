import os, time, shutil
from scipy import spatial

start = time.time()

toinsert_list = "platform_to_insert_step2.csv"

def insert_tiploc(f_seg, f_P, f_p, f_name):
    f_fin = open(f_seg)
    f_fout = open(f_seg + ".temp", "w")
    P_todo = 1
    p_todo = 1
    for f_line in f_fin:
        if f_line[:1].isdigit() or line[:1] == "#":
            f_lineT = f_line.split()
#            print(f_lineT[0],f_P,f_p)
            if float(f_lineT[0]) >= float(f_P):
                if P_todo:
                    f_fout.write(f_P + "\tf\t0\tP\t" + f_name + "\n")
                    P_todo = 0
                    f_fout.write(f_line)
                elif float(f_lineT[0]) >= float(f_p):
                    if p_todo:
                        f_fout.write(f_p + "\tf\t0\tp\t" + f_name + "\n")
                        p_todo = 0
                        f_fout.write(f_line)
                    else:
                        f_fout.write(f_line)
                else:
                    f_fout.write(f_line)
            else:
               f_fout.write(f_line)                                
        else:
            f_fout.write(f_line)
            
    f_fin.close()
    f_fout.close()

    shutil.move((f_seg + ".temp"), f_seg)
    
    
fin = open(toinsert_list)

for line in fin:
    lineT = line.split(',')
    segment_name = lineT[0]
    P_km = lineT[1]
    p_km = lineT[3]
    pf_name = lineT[5]

    print(segment_name, P_km, p_km, pf_name)

    insert_tiploc(segment_name, P_km, p_km, pf_name)

fin.close()

end = time.time()
print('Completed computing in: ', round(end-start, 2),'s')
