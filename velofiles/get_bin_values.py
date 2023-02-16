import numpy as np
# import scipy
# import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector as ms
import pyodbc
# import boxsdk

file = pd.read_csv('Stars_APA.csv').dropna()
# sn = file.ix[:,1]
# bin = file.ix[:,0]
# print(sn, bin)
# print(file.T.iteritems())

# CLIENT_ID = None
# CLIENT_SECRET = None
# ACCESS_TOKEN = None

# mydb = ms.connect(
#     host="127.0.0.1",
#     user="root",
#     password="root",
#     database="datalog"
# )
db = pyodbc.connect('Driver={SQL Server};'
                    'Server=vl-mes-db01.velodyne.com;'
                    'Database=labview;'
                    'Trusted_Connection=yes;')
# select = r"select `Serial#`, `Bin#`, `Vendor`, `Builder`, `Pass_Fail`, `Tray Placement Pos`, `Index`, `Date_Time`, `Tray Name` from `loadedmetrology` where `Tray Placement Pos` is NOT NULL or `Tray Placement Pos` != '' order by `Index` desc"
# mycursor = mydb.cursor()
# mycursor.execute(select)
cursor = db.cursor()
for row in file.T.iteritems():
    for n, i in enumerate(row[1]):
        if n%2 == 0:
            SN = str(i)[-8:-4]+'-'+str(i)[-4:]
        elif n%2 != 0:
            BV = i
    print(SN, BV)
    update = "update SnStatus set BinValue = {binn} where SerialNumber = \'{serial}\' \n".format(binn=BV, serial=SN)
    print(update)
    cursor.execute(update)
        # print(SN +': ' + BV)
    # SN, BV = str(row[0]), row[1]
    # print(SN)
    # SN = SN[-8:-4]+'-'+SN[-4::]
    # print(SN, BV)
    # if SN != "None":
    #     SN=str(SN)
    #     SN = SN[0:4]+"-"+SN[4:]
    #     try:
    #         BV = int(BV)
    #     except:
    #         BV = 0
    #     try:
    #         TrayPlace = int(TrayPlace)
    #     except:
    #         TrayPlace = 0
    #     print (SN, vendor, builder, BV)



# cursor.execute(update)
db.commit()
# mydb.close()