inputFile = "TDEF 955 10122014 123553.txt"
outputFile = "Timetables_20150108.txt"
tiploclistFile = "TIPLOC.csv" # -in format-: Name,TIPLOC

outputSQL = outputFile.replace('.txt','.sql')

import os, time

start_t = time.time()

print("converting raw timetable : " + inputFile)

topline = open(inputFile, "r").readlines()[0]
timetableStartDate = topline.split()[4].replace('-','/')
timetableEndDate = topline.split()[6].replace('-','/')

timetableID = 464
dop = '.MTWTF.'
sequence = 1

currentArr = '0:00:00'

    
tiploclist, tipnamelist = [],[]
ftiploc = open(tiploclistFile)
for t in ftiploc:
    tipnamelist.append(t.split(',')[0])
    tiploclist.append(t.split(',')[1].replace('\n',''))
#print(tiploclist)


fin = open(inputFile)
fout = open(outputFile, "w")

for line in fin:
    lineT = line.split()
    if lineT[0] == 'BID':
        fout.write('*StartTimetable\n*TimetableID\t' + str(timetableID) + '\n')
        fout.write('*HeadCode\t' + lineT[1] + '\n')
        fout.write('*DOP\t' + dop + '\n')

        timetableID = timetableID + 1

    elif lineT[0] == 'THD':
        desc = lineT[7] + '-' + lineT[9]
        departtime = lineT[8]
        if desc == 'EGS-STV':
            desc = 'Egersund-Stavanger'
            routeID = 108
            route = 'NSB~Egersund~Stavanger'
            
        elif desc == 'STV-EGS':
            desc = 'Stavanger-Egersund'
            routeID = 107
            route = 'NSB~Stavanger~Egersund'
            
        fout.write('*OperatingCode\t-\n*Description\t' + desc + '\n')
        fout.write('*Route\t' + route + '\n')
        fout.write('*RouteId\t' + str(routeID) + '\n')
        fout.write('*Depart\t' + departtime + '\n')
        fout.write('*StartDate\t' + timetableStartDate + '\n')
        fout.write('*EndDate\t' + timetableEndDate + '\n')

        currentEndST = lineT[9]

    elif lineT[0] == 'TMV':
        #currentST = lineT[3]
        currentST = tipnamelist[tiploclist.index(lineT[3])]
        currentDep = lineT[5]
        if currentArr != currentDep:
            fout.write(str(sequence) + '\t' + currentST + '\t' + currentArr + '\t' + currentDep + '\n')
            sequence = sequence + 1

        currentArr = lineT[6]
        
        
    elif lineT[0] == 'TSP' and lineT[3] == currentEndST:
        fout.write(str(sequence) + '\t' + tipnamelist[tiploclist.index(currentEndST)] + '\t' + currentArr + '\t0:00:00\n')
        fout.write('*EndTimetable\n\n\n')

        sequence = 1

fin.close()
fout.close()



## SET up NSB site Trial on the trial server for timetables
fin = open(outputFile)
fout = open(outputSQL, "w")

writestr = "\
BEGIN TRY\nBEGIN TRANSACTION\nBEGIN\n\n\
DECLARE @SitesId INT SELECT @SitesId = SitesId FROM [dbo].[Sites] WHERE SiteName = 'NSB';\n\
----------------------\n\
-- DECLARE SEGMENTS --\n\
----------------------\n\
DECLARE @NSB_Egersund_Stavanger INT SELECT @NSB_Egersund_Stavanger = SegmentsId FROM [dbo].[Segments] WHERE [dbo].[Segments].SegmentName = 'NSB~Egersund~Stavanger'\n\
DECLARE @NSB_Stavanger_Egersund INT SELECT @NSB_Stavanger_Egersund = SegmentsId FROM [dbo].[Segments] WHERE [dbo].[Segments].SegmentName = 'NSB~Stavanger~Egersund'\n\
----------------------\n\
-- DECLARE ROUTES --\n\
----------------------\n\
DECLARE @Route_Stavanger_Egersund INT\n\
DECLARE @Route_Egersund_Stavanger INT\n\
SELECT @Route_Stavanger_Egersund = 107\n\
SELECT @Route_Egersund_Stavanger = 108\n\
-----------------------\n\
-- INSERT TIMETABLES --\n\
-----------------------\n\
DECLARE @TimetablesId INT\n\n\
"
fout.write(writestr)

for line in fin:
    lineT = line.split()
    if len(lineT) > 0 and lineT[0] == '*TimetableID':
        TimetableID = lineT[1]
    elif len(lineT) > 0 and lineT[0] == '*HeadCode':
        HeadCode = lineT[1]
    elif len(lineT) > 0 and lineT[0] == '*DOP':
        DOP = lineT[1]
    elif len(lineT) > 0 and lineT[0] == '*Description':
        if lineT[1] == 'Egersund-Stavanger':
            Route = '@Route_Egersund_Stavanger'
        elif lineT[1] == 'Stavanger-Egersund':
            Route = '@Route_Stavanger_Egersund'
    elif len(lineT) > 0 and lineT[0] == '*Depart':
        Depart = lineT[1]
    elif len(lineT) > 0 and lineT[0] == '*StartDate':
        StartDate = '2014-12-14' #lineT[1].replace('/','-')
    elif len(lineT) > 0 and lineT[0] == '*EndDate':
        EndDate = '2015-12-12' #lineT[1].replace('/','-')
        writestr ="\n\
INSERT INTO [dbo].[Timetables]([RoutesId],[HeadCode],[OperatingCode],[DOP],[StartDate],[EndDate],\
[Visible],[SitesId],[ExternalId],[OverlayId],[OriginalId],[LastEditedDate],[CreateDate],[ExtractType])\n\
VALUES(" + Route + ",'" + HeadCode + "' ,'-','" + DOP + "','" + StartDate + " 00:00:00.000','" + EndDate + " 00:00:00.000',\
1,@SitesId,NULL,NULL,NULL,GETDATE(),GETDATE(),'F')\n\
SELECT @TimetablesId = @@IDENTITY\n\n"
        
        fout.write(writestr)

    elif len(lineT) > 0 and lineT[0][:1].isdigit():
        lineTL = line.split('\t')
        if lineTL[2][:2] == '24':
            arrTime = '00' + lineTL[2][2:]
            defaultAdate = '1900-01-02 '
        else:
            arrTime = lineTL[2]
            defaultAdate = '1900-01-01 '
        if lineTL[3][:2] == '24':
            depTime = '00' + lineTL[3][2:]
            defaultDdate = '1900-01-02 '
        else:
            depTime = lineTL[3]
            defaultDdate = '1900-01-01 '


        writestr ="\
INSERT INTO [dbo].[TimetableLegs]([TimetablesId],[Station],[ArrivalTime],[DepartTime],[StoppingLocation],\
[SequenceNo],[MidnightRollOver],[SegmentsId],[MajorLocation],[LineName],[LineCode],[Platform],[TiplocCode])\n\
VALUES(@TimetablesId,'" + lineTL[1] + "','" + defaultAdate + arrTime + ".000','" + defaultDdate + depTime.replace('\n','') + ".000',1," + lineTL[0] + ",0," + Route + "\
,0,null,null,null,null)\n"

        fout.write(writestr)


writestr = "\n\
END\n\
COMMIT TRANSACTION  print 'COMMIT'\n\
END TRY\n\
BEGIN CATCH\n\
IF @@TRANCOUNT > 0\n\
SELECT ERROR_MESSAGE() AS ErrorMessage;\n\
ROLLBACK  TRANSACTION  print 'ROLLBACK'\n\
END CATCH"
fout.write(writestr)

fin.close()
fout.close()

end_t = time.time()
print('Completed computing in: ', round(end_t-start_t, 2),'s')
