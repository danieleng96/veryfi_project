# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import wolframalpha
#
# hex = '13e7'
# print(int(hex,16),type(int(hex,16)))

# class wolfra
# malpha.Client(app_id):
# #     def __init__(self, app_id):


# # Fixing random state for reproducibility
# np.random.seed(19680801)
#
#
# # Create new Figure and an Axes which fills it.
# fig = plt.figure(figsize=(7, 7))
# ax = fig.add_axes([0, 0, 1, 1], frameon=False)
# ax.set_xlim(0, 1), ax.set_xticks([])
# ax.set_ylim(0, 1), ax.set_yticks([])
#
# # Create rain data
# n_drops = 50
# rain_drops = np.zeros(n_drops, dtype=[('position', float, 2),
#                                       ('size',     float, 1),
#                                       ('growth',   float, 1),
#                                       ('color',    float, 4)])
#
# # Initialize the raindrops in random positions and with
# # random growth rates.
# rain_drops['position'] = np.random.uniform(0, 1, (n_drops, 2))
# rain_drops['growth'] = np.random.uniform(50, 200, n_drops)
#
# # Construct the scatter which we will update during animation
# # as the raindrops develop.
# scat = ax.scatter(rain_drops['position'][:, 0], rain_drops['position'][:, 1],
#                   s=rain_drops['size'], lw=0.5, edgecolors=rain_drops['color'],
#                   facecolors='none')
#
#
# def update(frame_number):
#     # Get an index which we can use to re-spawn the oldest raindrop.
#     current_index = frame_number % n_drops
#
#     # Make all colors more transparent as time progresses.
#     rain_drops['color'][:, 3] -= 1.0/len(rain_drops)
#     rain_drops['color'][:, 3] = np.clip(rain_drops['color'][:, 3], 0, 1)
#
#     # Make all circles bigger.
#     rain_drops['size'] += rain_drops['growth']
#
#     # Pick a new position for oldest rain drop, resetting its size,
#     # color and growth factor.
#     rain_drops['position'][current_index] = np.random.uniform(0, 1, 2)
#     rain_drops['size'][current_index] = 5
#     rain_drops['color'][current_index] = (0, 0, 0, 1)
#     rain_drops['growth'][current_index] = np.random.uniform(50, 200)
#
#     # Update the scatter collection, with the new colors, sizes and positions.
#     scat.set_edgecolors(rain_drops['color'])
#     scat.set_sizes(rain_drops['size'])
#     scat.set_offsets(rain_drops['position'])
#
#
# # Construct the animation, using the update function as the animation director.
# animation = FuncAnimation(fig, update, interval=10)
# plt.show()

import numpy as np
# import pandas as pd
# failure_reason = 'FAIL'
# data_df = pd.DataFrame({'FailureReason' : ['Fail', '', '', 'Fail'],'B' : ['Fail ', 'F', '', 'Fail']})
# # print(test)
# # if test[(test.A)] == '':
# data_df['FailureReason'][(data_df['FailureReason'] != '')] = data_df['FailureReason'][(data_df['FailureReason'] != '')].astype(str) + ',' + failure_reason
# data_df['FailureReason'][(data_df['FailureReason'] == '')] = data_df['FailureReason'][(data_df['FailureReason'] == '')].astype(str) + failure_reason
# # data_df['FailureReason'][(data_df['FailureReason'] != '')] = data_df['FailureReason'][(data_df['FailureReason'] != '')].astype(str) + ',' + failure_reason
#
#     # test['A'] = test['A'] + 'TROSA_FAIL'
# print(data_df)
import pandas as pd
from APD_breakdown import SQL_server

sql = SQL_server.py_sql()
# print(sql.sn_search('L260-1608'))
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt

df = sql.sn_search('L260-1608')

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Python ")

        # setting geometry
        self.setGeometry(100, 100, 600, 400)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method for widgets
    def UiComponents(self):
        # creating push button
        button = QPushButton("Geek Button", self)

        # setting geometry of the push button
        button.setGeometry(200, 150, 100, 40)

        # setting background color to push button when mouse hover over it
        button.setStyleSheet("QPushButton::hover{background-color : lightgreen;}")


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
class pandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     model = pandasModel(df)
#     view = QTableView()
#     view.setModel(model)
#     # view.resize(800, 600)
#     view.show()
#     sys.exit(app.exec_())
# bd = [0,-181,-182,0]
# data_df = pd.DataFrame(data = [[0,'',-170],[0,'',-180],[0,'',-182],[0,'',-170],[0,'',-194],[0,'',-140],[0,'',-185],[0,'',-171]], columns = ['Failed','FailureReason','Temp_Compensated_V'])
# # data_df = pd.DataFrame(data = [[0,'',-160],[0,'',-180],[0,'',-202],[0,'',-170],[0,'',-168],[0,'',-182],[0,'',-185],[0,'',-171]], columns = ['Failed','FailureReason','Temp_Compensated_V'])
# #
# # # print(data_df)
# # def Spread(data_df):
#
# a = 3
# b = 4
# c = [a, b]
# def test(a,b):
#     return f"{a} followed by {b}"
#
# print(test(a,b))
#
# #     data_df = data_df.sort_values(by = 'Temp_Compensated_V')
# #     bd = data_df['Temp_Compensated_V']
# #     # deltas = [0]
# #     def MaxDiff(bd):
# #         dmax = 0
# #         vmin = bd.iloc[0]
# #         for i in range(len(bd)):
# #             if (bd.iloc[i] < vmin):
# #                 vmin = bd.iloc[i]
# #             elif (bd.iloc[i] - vmin > dmax):
# #                 # ind.append(i)
# #                 dmax = bd.iloc[i] - vmin
# #         return dmax
# #     ind = [0]
# #     dmax = MaxDiff(bd)
# #     if dmax > 5:
# #         new_sum = 0
# #         deltas = [0]
# #         for i in range((len(bd)) - 1):
# #             delt = (bd.iloc[i + 1] - bd.iloc[i])
# #             deltas.append(delt)
# #             new_sum = new_sum + delt
# #             if new_sum > 5:
# #                 new_sum = 0
# #                 ind.append(i+1)
# #         ind.append(len(bd))
# #         length = 0
# #         span = 0
# #         for n in range(len(ind)-1):
# #             slice = bd.iloc[ind[n]:ind[n+1]]
# #             length_each = len(slice)
# #             if length_each > length:
# #                 main_slice = slice
# #                 length = length_each
# #             elif length_each == length:
# #                 if span > MaxDiff(slice):
# #                     main_slice = slice
# #                     length = length_each
# #                 else:
# #                     length = length_each
# #             else:
# #                 length = length_each
# #             span = MaxDiff(slice)
# #
# #         data_df = data_df.assign(Failed = 1)
# #
# #         for each in main_slice.index:
# #             data_df.at[each, 'Failed'] = 0
# #         data_df = data_df.sort_index()
# #
# #         failure_reason = 'Ch_Spread>5V'
# #         data_df['FailureReason'][(data_df['FailureReason'] != '')] = data_df['FailureReason'][
# #                                                                          (data_df['FailureReason'] != '')].astype(
# #             str) + ',' + failure_reason
# #         data_df['FailureReason'][(data_df['FailureReason'] == '')] = data_df['FailureReason'][
# #                                                                          (data_df['FailureReason'] == '')].astype(
# #             str) + failure_reason
# #     return dmax, data_df
#
# # print(Spread(data_df))