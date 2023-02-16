import pyodbc

user = 'VL_STARS'
pwd = r'irtfs5#935'
server = 'vl-mes.database.windows.net'
db = 'labview2'
trusted = 'no'

dbo = pyodbc.connect('Driver={SQL Server};'
                          'Server=%s;'
                          'Database=%s;'
                          'UID=VL_STARS;'
                          'PWD=irtfs5#935;'
                          'Trusted_Connection=no;' % (server, db))

cursor = dbo.cursor()
for row in cursor.execute("select * From dbo.TROSA_101_InitialTestingLD_AsicLpTest_CH"):
    print(row)