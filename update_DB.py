import pyodbc, time
start_t = time.time()
 
DBfile = 'C:\\Zhao\\job\\NR_Database\\FSR_DATA_05_09_2011_HZ.mdb'
#table = 'Stations'
#table = 'Signals'
#table = 'Junctions'
table = 'Mileposts'


#table = 'TrackCentreline'
#where = " where ELR = 'HMN2'"
where = ""

connStr = 'Driver={Microsoft Access Driver (*.mdb)};DBQ=' + DBfile + ';'

conn = pyodbc.connect(connStr)
cursor = conn.cursor()
cursor1 = conn.cursor()

updateLong = ''
updateLat = ''

SQL = "SELECT ACCESS_ID, LATITUDE, LONGITUDE, LAT, LONG FROM " + table + where + ";"
print(SQL)
for row in cursor.execute(SQL): # cursors are iterable
    
#    print (float(row[3].split()[1]))

    if (row[1] is None) or (len(row[1]) == 0):
        pass
    else:
        tempStr = row[1].split()
        if tempStr[0] == 'N':
            updateLat = str(float(row[1].split()[1]))
        elif tempStr[0] == 'S':
            updateLat = str(-1*float(row[1].split()[1]))

    if (row[2] is None) or (len(row[2]) == 0):
        pass
    else:
        tempStr = row[2].split()
        if tempStr[0] == 'E':
            updateLong = str(float(row[2].split()[1]))
        elif tempStr[0] == 'W':
            updateLong = str(-1*float(row[2].split()[1]))
    
    SQL1 = "UPDATE " + table + " SET " + table + ".LAT = " + updateLat + ", " + table + ".[LONG] = " + updateLong + " WHERE ACCESS_ID = " + str(row[0]) + ";"

#    print(SQL1)
    cursor1.execute(SQL1)
#    print(row)
 
cursor.close()
conn.commit()
conn.close()

end_t = time.time()
print('Completed computing in: ', round(end_t-start_t, 2),'s')
