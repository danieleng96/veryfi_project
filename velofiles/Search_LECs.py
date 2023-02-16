import pyodbc
import numpy as np
import pandas as pd
import csv

path = 'C:/Users/deng/Downloads/'
LEC = pd.read_csv(path+r'LEC and TROSA Inforrmation.csv', usecols = [0,1,3,4,5], header = 1).applymap(str)
sns = pd.read_csv(path+'serial_list_3dev.csv', usecols = [1]).applymap(str)
LEC.dropna()
# print(LEC['TROSA Serial no:'].dropna())
LEC['TROSA Serial no:'] = LEC['TROSA Serial no:'].dropna().apply(lambda x:x[-9:])
sns.squeeze()
# print(type(LEC['TROSA Serial no:']),type(sns['serial with outlier']))
L = LEC['TROSA Serial no:']
s = sns['serial with outlier']
intersection = pd.Series(np.intersect1d(L, s))
print(intersection)