#"SNCF_xml2tt_0.3.py" convers SNCF .xml timetable into .tt format in UTF-8 encoding
#last updated on 09/10/2014, output distance column using KP locations in .route

inputxmllist = 'SNCF_xml2tt_0.3_input_list.txt'

default_dewell = 300

import os, time, datetime, codecs, inspect, re
import xml.etree.ElementTree as ET



def getkpdistance(kp, ligne, routelinelist):
    global globalligne
    if ligne == '0':
        print(str(kp) + 'kp, ERROR: ligne value is 0, assume same as previous: ' + globalligne)
        #return 999.999
        ligne = globalligne
    else:
        globalligne = ligne
        
    kplist, dislist = [],[]
    for line in routelinelist:
        if line[2].replace('L','') == ligne:
            dislist.append(float(line[0]))
            kplist.append(float(line[1]))
    closestkp = min(kplist, key=lambda x:abs(x-kp))

    #distance = round(dislist[kplist.index(closestkp)] - closestkp + kp, 3) #use this for same decimal
    distance = round(dislist[kplist.index(closestkp)], 3)   #use this for different decimal

    #print(distance, kp, closestkp, ligne, len(kplist))
    return distance



start_t = time.time()
xmlfilelist, routefilelist = [],[]

fin = open(inputxmllist)
for line in fin:
    if line[0] <> "#":
        xmlfilelist.append(line.split()[0])
        routefilelist.append(line.split()[1].replace('\n',''))
#print(xmlfilelist,routefilelist)

globalligne = ''

for currentxmlfile in xmlfilelist:
    print('processing: ' + currentxmlfile)
    tree = ET.parse(currentxmlfile)
    root = tree.getroot()

    currentroutefile = routefilelist[xmlfilelist.index(currentxmlfile)]
    routelinelist, lignelist = [],[]
    froute = open(currentroutefile,'r')
    for line in froute:
        linet = line.split()
        if linet[2] == 'KP':
            routelinelist.append([line.split()[1], line.split()[3], line.split()[4].replace('\n','').replace('#','L')])
            lignelist.append(line.split()[4].replace('\n','').replace('#','L'))
            
    froute.close()
    lignelist = set(lignelist)
    #print(len(routelinelist), routelinelist[0], len(lignelist), lignelist)

    fout = codecs.open(currentxmlfile.replace('xml','tt'), 'w',  'utf-8')
    fout.write("#encoding='UTF-8'\n#dist\tname\tearliest\tlatest\tdwell\n")

    root[0][0][10].text = root[0][0][9].text
    root[0][0][10].set('updated', 'yes')
    
    for PKOpti in root.iter('PKOpti'):

        earliest = PKOpti.find('harrMin').text
        latest = PKOpti.find('harrMax').text

        if latest == '0':
            latest = earliest

        if PKOpti.find('arret').text == "true":
            
            latest = earliest
            if PKOpti.find('hdep').text == '-1':
                PKOpti.find('hdep').text = earliest
            
            dewell = int(PKOpti.find('hdep').text) - int(PKOpti.find('harrMin').text)

            if abs(dewell) == int(PKOpti.find('hdep').text) or abs(dewell) == int(PKOpti.find('harrMin').text) or dewell == 0:
                dewell = default_dewell
        else:
            dewell = 0

        kproutedistance = getkpdistance(round(float(PKOpti.find('pk').text),3), PKOpti.find('ligne').text, routelinelist)
        
##        writestr = str(round(float(PKOpti.find('distance').text)/1000,3)) + "\t" + PKOpti.find('cilib').text \
##        + "\t" + str(datetime.timedelta(seconds = int(earliest))) + "\t" + \
##        str(datetime.timedelta(seconds = int(latest))) + "\t" + str(dewell) + "\t" + PKOpti.find('pk').text + "\n"

        writestr = str(kproutedistance) + "\t" + PKOpti.find('cilib').text \
        + "\t" + str(datetime.timedelta(seconds = int(earliest))) + "\t" + \
        str(datetime.timedelta(seconds = int(latest))) + "\t" + str(dewell) + "\n"

        #print(writestr)

        fout.write(writestr)

    fout.close()
end_t = time.time()
print('Completed computing in: ' + str(round(end_t-start_t, 2)) + 's')
