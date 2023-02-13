import pyodbc
import sys
import config
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QInputDialog, QLineEdit, QWidget, QGridLayout, QPushButton, QApplication, QLabel,
                             QGroupBox, QVBoxLayout, QRadioButton, QLabel, QTableWidgetItem, QTableWidget, QMainWindow)
cont = 1

class GetInfo(QWidget):
    def __init__(self):
        super().__init__()


        layout = QVBoxLayout()
        self.label = QLabel("Get Tray Number")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.pixmap = QPixmap('APA.png')
        # adding image to label
        self.label.setPixmap(self.pixmap)
        # dialog = QInputDialog()
        # layout.addWidget(dialog)
        # tray_number, okPressed = QInputDialog.getText(self, "Enter Tray Number", "Tray Number:", QLineEdit.Normal, "")
        # if okPressed and tray_number != '' and tray_number:
        #     tray_command = "\'" + tray_number + "\'"
        #     return tray_command
        # else:
        #     return None

# class Get(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         def getTray(self):
#             tray_number, okPressed = QInputDialog.getText(self, "Enter Tray Number", "Tray Number:", QLineEdit.Normal,
#                                                           "")
#             if okPressed and tray_number != '' and tray_number:
#                 tray_command = "\'" + tray_number + "\'"
#                 return tray_command
#             else:
#                 return None


# class basicWindow(QMainWindow):
class basicWindow(QWidget):
    # colordic = {"AllPassed":"green","Passed":"lightgreen","Failed":"pink","Velobit":"yellow",None:"gray","Untested":"lightgray"}
    colordic = config.colordic
    today = config.colordic
    velobit_ch_rnd = config.velobit_ch_rnd
    # existing = 0

    def __init__(self, tray, product, loc = 0):
        super().__init__()
        self.location = config.location[loc]
        self.dimensions_dict = config.dimensions_dict
        self.rows_dict = config.rows_dict
        self.product = product
        self.w = GetInfo()
        self.tray_name = tray
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        # self.button = QPushButton("Push for Window")
        # self.button.clicked.connect(self.show_new_window)
        # self.setCentralWidget(self.button)

        # self.db = pyodbc.connect('Driver={SQL Server};'
        #                          'Server=vl-mes-db01.velodyne.com;'
        #                          'Database=labview;'
        #                          'Trusted_Connection=yes;')
        self.db = pyodbc.connect('Driver={SQL Server};'
                                 
                                 
                                 'Server=%s;'
                                 'Database=%s;'
                                 'UID=%s;'
                                 'PWD=%s;'
                                 'Trusted_Connection=%s;'%(self.location['server'], self.location['db'], self.location['user'],self.location['pwd'], self.location['trusted']))
        self.cursor = self.db.cursor()

        # print(find_tray_location)
        # find_tray_location = "SELECT SerialNumber from labview.dbo.SnStatus where TrayName = {tray_name} and TrayPlace = {tray_place}".format(tray_name = self.tray_name, tray_place=self.index)
        self.gui_build()

    # def show_new_window(self,checked):
    #     w = GetInfo()
    #     w.show()

    def gui_build(self):
        #takes data from test_data
        self.tray_name = self.initUI()
        # self.tray =
        # self.tray = self.test_data()[1]
        # vbox = QVBoxLayout()
        tableWidget = QTableWidget()
        # tableWidget.setGeometry(0,0,500,600)
        # tableWidget.setRowCount(6)
        # tableWidget.setColumnCount(5)
        # print(self.test_data)
        self.w.show()
        self.serials = [0]*(self.dimensions_dict[self.product][0]*self.dimensions_dict[self.product][1])
        for y in range(self.dimensions_dict[self.product][0]):
            for x in (range(self.dimensions_dict[self.product][1])):
                self.index = (self.dimensions_dict[self.product][1] * y + x + 1)
                # print(self.index)
                # tableWidget.setItem(y, x, QTableWidgetItem(self.dimensions_dict[self.product][1] * y + x + 1))
                self.cont = 1
                # self.index = (7 * x + y + 1)
                tableWidget.setItem(y, x, QTableWidgetItem(self.dimensions_dict[self.product][1] * y + x + 1))
                groupbox = QGroupBox()
                vbox = QVBoxLayout()
                groupbox.setLayout(vbox)
                groupbox.setStyleSheet("background-color: white")
                label_num = QLabel(str(self.index))
                vbox.addWidget(label_num)
                while self.cont == 1:
                    sn = self.getSN(self.index)
                self.serials[self.index-1] = sn
                # print(self.serials)

                label = QLabel("New: {SN}".format(SN=sn))
                self.existing = self.check_each_number()
                groupbox.setStyleSheet("background-color: lightblue")
                if self.existing:
                    if sn is None:
                        groupbox.setStyleSheet("background-color: lightgreen")
                        exist = QLabel("{existing}".format(existing=self.existing))
                    else:
                        exist = QLabel("Old: {existing}".format(existing = self.existing))
                        groupbox.setStyleSheet("background: QLinearGradient(spread:pad,x1:0 y1:0, x2:1 y2:0, stop:0 #8CF3C6, stop:1 #EC95F6)")
                        vbox.addWidget(label)
                    vbox.addWidget(exist)

                self.grid_layout.addWidget(groupbox, y, x)
                if sn != None and not self.existing:
                    groupbox.setStyleSheet("background-color: {color}".format(color="yellow"))
                    vbox.addWidget(label)

        self.w.close()
        self.tray_button = QPushButton("New Tray")
        self.check_all = QPushButton("Check in all")
        self.check_all.setStyleSheet('background-color: pink')
        self.tray_button.setStyleSheet('background-color: orange')

        self.UiComponents()
        self.grid_layout.addWidget(self.check_all)
        self.grid_layout.addWidget(self.tray_button)
        # self.grid_layout.addWidget(self.refresh_button)
        self.setGeometry(50,50,500,600)
        # self.grid_layout.addWidget((self.send_email))
        self.setWindowTitle('TRAY {tray}'.format(tray=self.tray_name))
    def check_each_number(self):
        find_tray_location = 'WITH most_recent AS (SELECT SerialNumber, ProductName,' \
                             '' \
                             ' TrayPlace, TrayName, ROW_NUMBER() OVER (PARTITION BY TrayPlace ORDER BY TStamp DESC) AS rn FROM {db}.dbo.SnStatus AS s) Select SerialNumber, TrayPlace, TrayName, rn from most_recent Where TrayName = {tray_name} and ProductName = \'{product}\' and TrayPlace = \'{tray_place}\' Order by TrayPlace'.format(
            tray_name=self.tray_name, tray_place =self.index, product = self.product, db = self.location['db'])
        # print(find_tray_location)
        # find_tray_location = "SELECT SerialNumber from labview.dbo.SnStatus where TrayName = {tray_name} and TrayPlace = {tray_place}".format(tray_name = self.tray_name, tray_place=self.index)
        raw = self.cursor.execute(find_tray_location)
        for line in raw:
            return line[0]


    def initUI(self):
        self.product = self.getProduct()
        print(self.product)
        self.tables = self.getTables(self.product)
        print(self.tables)
        self.tray =  self.getTray()
        if self.tray:
            return self.tray
            self.show()
        else:
            quit()

    def getTray(self):
        tray_number, okPressed = QInputDialog.getText(self, "Enter Tray", "Tray Number:", QLineEdit.Normal, "")
        if okPressed and tray_number != '' and tray_number:
            tray_command = "\'"+tray_number+"\'"
            return tray_command
        else:
            return None
    def getSN(self, tray_place):
        self.cont = 0
        SN, okPressed = QInputDialog.getText(self, "{place} Enter Serial Number".format(place = tray_place), "SN {tray_place}:".format(tray_place=tray_place), QLineEdit.Normal, "")
        if okPressed and SN != '':
            SN = "\'"+SN.replace(" ", "")+"\'"
            if len(SN) == 10 and SN[1].isalpha() == True:
                return SN[:5]+'-'+SN[5:]
            elif len(SN) == 11 and SN[1].isalpha() == True:
                return SN
            elif SN is None:
                return SN
            else:
                print("Not valid, please enter a serial number in the form A###-#### or A#######")
                self.cont = 1
                return None

    def getProduct(self):
        #used with AddComment, gets column names
        get_prod = "Select ProductName from {db}.dbo.Products".format(db = self.location['db'])
        raw = self.cursor.execute(get_prod)
        # raw = pd.read_sql(column_command, self.db)
        prods = []
        for row in raw:
            prod = str(row[0])
            if prod:
                prods.append(prod)
            else:
                print("None")
        product,okPressed = QInputDialog.getItem(self, "Select Product","Products", prods, 0, False)
        if okPressed and product:
            return product

    def getTables(self, product):
        #take all CH table that this database has for this product,input the product
        tables = 'select name from sysobjects where xtype = \'U\' and right(name,2) = \'CH\' and left(name,len(\'{product}\')) = \'{product}\''.format(db = self.location['db'], product = product)
        print(tables)
        raw = self.cursor.execute(tables)
        tests = []
        for test in raw:
            tests.append(test)
        return tests

    def getColumn(self, sn):
        #used with AddComment, gets column names
        column_command = "Select COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'TROSA_tracker\' AND TABLE_SCHEMA = \'dbo\' AND COLUMN_NAME LIKE \'COMMENT%\' AND COLUMN_NAME NOT LIKE \'%QC\'"
        raw = self.cursor.execute(column_command)
        # raw = pd.read_sql(column_command, self.db)
        columns = []
        for row in raw:
            column = str(row[0])
            if column:
                columns.append(column)
            else:
                print("None")
        station,okPressed = QInputDialog.getItem(self, "Test to comment","Tests", columns, 0, False)
        if okPressed and station:
            select_existing = "SELECT ISNULL(\n(SELECT {station} FROM TROSA_tracker WHERE SerialNumber = \'{SN}\'),\'\')".format(station = station, SN = sn)
            raw = self.cursor.execute(select_existing)
            for row in raw:
                select_comment = str(row[0])

            return station, select_comment
        else:
            return station, ""
    def getChoice(self):
        recent_trays = 'SELECT Distinct TrayName FROM [{db}].[dbo].[SnStatus] where ProductName = \'{product}\' order by TrayName desc'.format(product = self.product, db = self.location['db'])
        # recent_trays = 'SELECT Distinct TOP (100) TrayName FROM [labview].[dbo].[SnStatus]'
        raw = self.cursor.execute(recent_trays)
        tray_choice = ['Manually enter tray number']
        for row in raw:
            tray = str(row[0])
            if tray != "None" or tray is not None:
                tray_choice.append(tray)

        item, okPressed = QInputDialog.getItem(self, "Get Tray","Tray:", tray_choice, 0, False)
        if okPressed and item and item != 'Enter Tray Number':
            item = "\'"+item+"\'"
            return item
        elif okPressed and item == 'Manually enter tray number':
            return self.getTray()

    # def getChoice(self):
    #     recent_trays = 'SELECT Distinct TrayName FROM [labview].[dbo].[SnStatus] order by TrayName desc'
    #     # recent_trays = 'SELECT Distinct TOP (100) TrayName FROM [labview].[dbo].[SnStatus]'
    #     raw = self.cursor.execute(recent_trays)
    #     tray_choice = ['Manually enter tray number']
    #     for row in raw:
    #         tray = str(row[0])
    #         if tray != "None" or tray is not None:
    #             tray_choice.append(tray)
    #
    #     item, okPressed = QInputDialog.getItem(self, "Get Tray","Tray:", tray_choice, 0, False)
    #     if okPressed and item and item != 'Manually enter tray number':
    #         item = "\'"+item+"\'"
    #         return item
    #     elif okPressed and item == 'Manually enter tray number':
    #         return self.getTray()
    def test_data(self):
        #formerly init, pulls based on tray name input
        if self.tray_name is None:
            self.tray_name = self.initUI()
        # print(self.tray_name)
        self.grid = [None] * self.dimensions_dict[self.product][0]*self.dimensions_dict[self.product][1]
        # get_tray = 'Select SerialNumber, TrayPlace from labview.dbo.SnStatus Where TrayName = {tray_name} Order by TrayPlace'.format(
        #     tray_name=self.tray_name)
        get_tray = 'WITH most_recent AS (SELECT SerialNumber, TrayPlace, BinValue, ROW_NUMBER() OVER (PARTITION BY TrayPlace ORDER BY TStamp DESC) AS rn FROM {db}.dbo.SnStatus AS s) Select SerialNumber, TrayPlace, BinValue from most_recent Where TrayName = {tray_name} and rn = 1 Order by TrayPlace'.format(
            tray_name=self.tray_name, db = self.location['db'])
        self.Serials = []
        #put serial numbers in tray location in grid.
        for row in self.cursor.execute(get_tray):
            self.Serials.append(row[0])
            self.grid[int(row[1]) - 1] = row[0]
        return self.get_sn_data(0)

    def pull_most_recent(self, table, columns, SN, use_today=0):
        #feeds into get_sn_data
        self.table = table
        self.columns = columns
        self.SN = SN
        self.use_today = self.today[use_today]
        self.most_recent = 'WITH most_recent AS (SELECT m.*, ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TestIndex DESC) AS rn \
                  FROM {db}.dbo.{table} as m) Select {columns} from most_recent WHERE rn < 9 and SerialNumber = {SN} {t} Order by TestIndex desc \
                '.format(table=self.table, columns=self.columns, SN=self.SN, t=self.use_today, db = self.location['db'])
        raw = self.cursor.execute(self.most_recent)
        data = []
        for row in raw:
            fail = int(row[0])
            data.append(fail)
        if sum(data) == 0 and len(data) > 0:
            tag = "Passed"
        elif sum(data) != 0 and data[int(self.velobit_ch_rnd - 1)] == 0:
            # tag = "Velobit (Passed Ch{ch})".format(ch = self.velobit_ch_rnd)
            tag = "Velobit"
            # (Passed Ch{ch})".format(ch=self.velobit_ch_rnd)
        elif len(data) == 0:
            tag = "Untested"
        else:
            tag = "Failed"
        return data, tag

    def get_sn_data(self, today=0):
        #gets all SNs in single tray, gets data.
        for SN in self.grid:
            if SN is not None:
                test_list = []
                self.grid[self.grid.index(SN)].append(SN)
                for table in self.tables:
                    data, tag = self.pull_most_recent(table, 'Failed',
                                                          '\'{SN}\''.format(SN=SN),today)
                    self.grid[self.grid.index(SN)].append([table,tag])
                # self.grid[self.grid.index(SN)] = [SN, self.tlp, self.tbb, self.tapd, self.tf]
                # self.LP, self.tlp = self.pull_most_recent('TROSA_101_InitialTestingLD_AsicLpTest_CH', 'Failed',
                #                                           '\'{SN}\''.format(SN=SN), today)
                # self.APD, self.tapd = self.pull_most_recent('TROSA_101_InitialTestingAPD_ApdLifeTest_CH', 'Failed',
                #                                             '\'{SN}\''.format(SN=SN), today)
                # self.BB, self.tbb = self.pull_most_recent('TROSA_101_InitialTestingLD_BootBiasCal_CH', 'Failed',
                #                                           '\'{SN}\''.format(SN=SN), today)
                # self.F, self.tf = self.pull_most_recent('TROSA_101_FinalTestingLD_FinalTestLD_CH', 'Failed',
                #                                         '\'{SN}\''.format(SN=SN), today)
                # self.grid[self.grid.index(SN)] = [SN, self.tlp, self.tbb, self.tapd, self.tf]
        return self.grid, self.tray_name


    def UiComponents(self):
        self.tray_button.clicked.connect(self.clickme_new_tray)
        # self.refresh_button.clicked.connect(self.clickme_refresh)
        self.check_all.clicked.connect(self.Check_in_APA)
        # self.send_email.clicked.connect(self.clickme_send_email)

    def clickme_new_tray(self):
        self.tray_button.setStyleSheet('background-color: yellow')
        self.tray_button.setText('Enter New Tray')
        self.New = basicWindow(None,None)
        self.New.show()
        self.close()

    def clickme_refresh(self):
        # self.refresh_button.setStyleSheet('background-color: yellow')
        # self.refresh_button.setText('Refreshing')
        self.New = basicWindow(self.tray_name)
        self.New.show()
        self.close()

    def Check_in_APA(self):
        self.check_all.setStyleSheet('background-color: yellow')
        self.check_all.setText('Checking in')
        for i, sn in enumerate(self.serials):
            if sn:
                print(sn)
                insert_APA = 'IF(NOT EXISTS(SELECT SerialNumber from {db}.dbo.SnStatus where SerialNumber = {SN}))\nBEGIN\n\t' \
                             'INSERT INTO {db}.dbo.SnStatus (SerialNumber, ProductName, Location, Status, TrayName, TrayPlace) VALUES ({SN},\'{product}\',\'WIP1\',\'Production\', {tray}, \'{tray_place}\')' \
                             '\nEND\nELSE\nBEGIN\n\tUPDATE {db}.dbo.SnStatus\n\tSET TrayName = {tray}, TrayPlace = \'{tray_place}\', TStamp = default\nwhere SerialNumber = {SN}\nEND'.format(
                    tray=self.tray_name, SN=sn, product = self.product, tray_place=i + 1, db = self.location['db'])
                # insert_APA ='INSERT INTO labview.dbo.SnStatus (SerialNumber, ProductName, Location, Status, TrayName, TrayPlace)\nVALUES ({SN},\'{product}\',\'WIP1\',\'Production\', {tray}, \'{tray_place}\') ON DUPLICATE KEY UPDATE TrayName ={tray}, TrayPlace=\'{tray_place}\';'.format(product = self.product, tray = self.tray_name,  SN = sn, tray_place = i + 1)
                # print(insert_APA)
                self.cursor.execute(insert_APA)
        self.db.commit()
        self.New = basicWindow(self.tray_name,None)
        self.New.show()
        self.close()

    # def clickme_send_email(self):
    #     self.send_button.setStyleSheet('background-color: green')
    #     self.send_button.setText('Sending')
    #     self.grid_dataframe = pd.DataFrame.from_dict(self.grid)
    #     print(self.grid_dataframe.isnull())
    #     print("a")
    #     self.New = basicWindow(self.tray_name)
    #     self.New.show()
    #     self.close()
if __name__ == '__main__':

    windows = []
    refresh = 0
    app = QApplication(sys.argv)
    windows.append(basicWindow(None,None))
    windows[refresh].show()
    sys.exit(app.exec_())