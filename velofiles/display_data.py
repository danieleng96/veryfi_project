import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, \
    QPushButton, QItemDelegate, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from APD_breakdown import SQL_server

sql = SQL_server.py_sql()
# print(sql.sn_search('L260-1608'))
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt
#
#
#
#
# # class FloatDelegate(QItemDelegate):
# #     def __init__(self, parent=None):
# #         super().__init__()
# #
# #     def createEditor(self, parent, option, index):
# #         editor = QLineEdit(parent)
# #         editor.setValidator(QDoubleValidator())
# #         return editor
#
#
# class TableWidget(QTableWidget):
#     def __init__(self, df):
#         super().__init__()
#         self.df = df
#         self.setStyleSheet('font-size: 15px;')
#
#         # set table dimension
#         nRows, nColumns = self.df.shape
#         self.setColumnCount(nColumns)
#         self.setRowCount(nRows)
#
#         self.setHorizontalHeaderLabels((self.df.columns))
#         self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#
#         # self.setItemDelegateForColumn(1, FloatDelegate())
#
#         # data insertion
#         for i in range(self.rowCount()):
#             for j in range(self.columnCount()):
#                 self.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))
#         #
#         # self.cellChanged[int, int].connect(self.updateDF)
#
#     # def updateDF(self, row, column):
#     #     text = self.item(row, column).text()
#     #     self.df.iloc[row, column] = text
#
#
# class DFEditor(QWidget):
#     # df = sql.sn_search('L260-1608')
#
#     def __init__(self, df):
#         super().__init__()
#         self.resize(600, 200)
#         self.df = df
#
#         mainLayout = QVBoxLayout()
#
#         self.table = TableWidget(self.df)
#         mainLayout.addWidget(self.table)
#
#         button_print = QPushButton('Open Full tray')
#         button_print.setStyleSheet('background-color: #d63c3c')
#         button_print.setStyleSheet('font-size: 15px')
#         button_print.clicked.connect(self.display_table)
#         mainLayout.addWidget(button_print)
#
#         button_export = QPushButton('Export to CSV file')
#         button_export.setStyleSheet('font-size: 15px')
#         button_export.clicked.connect(self.export_to_csv)
#         mainLayout.addWidget(button_export)
#
#         self.setLayout(mainLayout)
#
#     def display_table(self):
#         print(self.table.df)
#
#     def export_to_csv(self):
#         self.table.df.to_csv('Data export.csv', index=False)
#         print('CSV file exported.')
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#
#     demo = DFEditor(sql.sn_search('L260-1608'))
#     demo.show()
#
#     sys.exit(app.exec_())
class TableWidget(QTableWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.setStyleSheet('font-size: 15px;')

        # set table dimension
        nRows, nColumns = self.df.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)

        self.setHorizontalHeaderLabels((self.df.columns))
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # self.setItemDelegateForColumn(1, FloatDelegate())

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))
        #
        # self.cellChanged[int, int].connect(self.updateDF)

    # def updateDF(self, row, column):
    #     text = self.item(row, column).text()
    #     self.df.iloc[row, column] = text

class DFEditor(QWidget):

    def __init__(self, df):
        super().__init__()
        self.resize(500, 150)
        self.df = df
        self.tray = self.df.loc[0,'TrayName']
        self.product = self.df.loc[0,'ProductName']

        mainLayout = QVBoxLayout()

        self.table = TableWidget(self.df)
        mainLayout.addWidget(self.table)

        button_print = QPushButton('Open Full tray')
        button_print.setStyleSheet('background-color: #d63c3c')
        button_print.setStyleSheet('font-size: 15px')
        button_print.clicked.connect(self.display_table)
        mainLayout.addWidget(button_print)

        button_export = QPushButton('Export to CSV file')
        button_export.setStyleSheet('font-size: 15px')
        button_export.clicked.connect(self.export_to_csv)
        mainLayout.addWidget(button_export)

        self.setLayout(mainLayout)

    def display_table(self):
        # basicWindow(self.tray, self.product)
        print("J")
        # print(self.table.df)

    def export_to_csv(self):
        self.table.df.to_csv('Data export.csv', index=False)
        print('CSV file exported.')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = DFEditor(sql.sn_search('L260-1608'))
    demo.show()

    sys.exit(app.exec_())
