import csv
from datetime import datetime
import pyodbc
import mysql.connector as ms

# make a text file called sns.txt
# copy paste all serial numbers from email (format A1234567) into sns.txt file.
# run this script, this will generate a query to input into MS SQL
mydb = ms.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="datalog")
db = pyodbc.connect('Driver={SQL Server};'
                    'Server=vl-mes-db01.velodyne.com;'
                    'Database=labview;'
                    'Trusted_Connection=yes;')

# table = 'loadedmetrology'
select = "Select SerialNumber, TrayName, TrayPlace from labview.dbo.SnStatus"
cursor = db.cursor()
cursor.execute(select)
mycursor = mydb.cursor()

for row in mycursor:

    SN, BV, vendor, builder, tray_place, index, date, tray_name, product_name = row[0], row[1], row[2], row[3], row[4], \
                                                                                row[5], row[6], row[7]

    if SN != "None":
        SN = str(SN)
        if len(SN) == 8:
            SN = SN[0:4] + "-" + SN[4:]


            if product_name == 'APA':
                print(product_name)
            else:
                product_name = 'TROSA_101'
                insert = r"Insert into test (`SerialNumber`, `TrayName`, `TrayPlace`) values (`{SN}`, `{tray_name}`, `{tray_place}`".format(
                    SN=sn, tray_name=tray, tray_place=place)

            try:
                mycursor.execute(insert)
                print("inserting %s" % BV)
            except:
                print("already checked")
# cursor = db.cursor()
# cursor.execute(insert)
db.commit()
mydb.close()
# now = datetime.now()
# now = str(now)[:-3]
# with open('sns.txt', newline='') as csvfile:
#     lines = [line.rstrip() for line in csvfile]
#     for each in lines:
#         SN = each[0:4]+"-"+each[4::]
#         # query = "UPDATE labview.dbo.SnStatus SET Status = \'FBN_FAI_Samples\' WHERE SerialNumber = \'"+SN+"\'"
#         query = "INSERT INTO labview.dbo.SnStatus (SerialNumber, ProductName, Location, Status, TStamp) \n VALUES (\'{serial}\', \'TROSA_101\', \'WIP1\', \'Production\', \'{time}\')".format(serial = SN, time=now)
#         print(query)