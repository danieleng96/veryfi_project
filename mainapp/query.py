q = 'CREATE TABLE Glob_Top_Live_Current_Read (\nID int identity(1,1) PRIMARYKEY,\
\nBoard_Name varchar(64) NOT NULL, \
\nTStamp_start_scan datetime DEFAULT getdate(),'\
    '\nScan_Number int NULL DEFAULT ROWNUMBER() over (partition by Board_Name),'
for i in range(64):
    q += f'Ch{i+1}_current float NULL, \n'
q+= ');'


import matplotlib.pyplot as plt
import numpy as np
import 