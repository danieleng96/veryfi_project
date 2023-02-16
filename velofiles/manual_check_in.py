import pyodbc
import datetime
import csv
import numpy as np
import pandas as pd
import glob
import os
import boxsdk

client = boxsdk.DevelopmentClient()
me = client.user().get()


db = pyodbc.connect('Driver={SQL Server};'
                    'Server=vl-mes-db01.velodyne.com;'
                    'Database=labview;'
                    'Trusted_Connection=yes;')

status = 'Velabit'
# now = datetime.now()
# now = str(now)[:-3]

path = 'C:\\Users\\deng\\Box\\TROSA Metrology'
# path = 'C:\\Users\\deng\\Documents'

files = glob.glob(path + '/*.xls')
files = files[-1::]
# sorted = files.sort(key=os.path.getmtime)
print(files)
cols0 = ['Bin Value','SN','Tray Name','TROSA Placement Pos']
cols1 = ['Bin#','Serial#','Tray Name','Tray Placement Pos']
for file in files:

    data = pd.read_excel(file)
    data.dropna()
    print('1:',data)
    # except:
    #     data = pd.read_excel(file, names = cols1)
    #     data.dropna()
    #     print('2:',data)
# pd.read_csv()
# with open('sns.txt', newline='') as csvfile:
#     lines = [line.rstrip() for line in csvfile]
#     for each in lines:
#         SN = each[0:4]+"-"+each[4::]
#         # query = "UPDATE labview.dbo.SnStatus SET Status = \'FBN_FAI_Samples\' WHERE SerialNumber = \'"+SN+"\'"
#         query = "INSERT INTO labview.dbo.SnStatus (SerialNumber, ProductName, Location, Status, TrayName, TrayPlace) \n VALUES (\'{serial}\', \'TROSA_101\', \'WIP1\', \'{status}\', \'{tray}\' , \'{place}\')".format(serial = SN, status = status, tray = tray, place = trayplace)
#         print(query)