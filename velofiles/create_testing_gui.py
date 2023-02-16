import pyodbc
import sys
import config
from itertools import groupby
import matplotlib.pyplot as plt
import time
import numpy as np
import pandas as pd
import smtplib
import APD_breakdown
import APD_breakdown.APD_breakdown_test as APD
from PyQt5.QtWidgets import (QInputDialog, QLineEdit, QGridLayout, QPushButton, QApplication,
                             QGroupBox, QVBoxLayout, QLabel, QTableWidgetItem, QTableWidget)
import traceback
cont = 1

class basicWindow(QTableWidget):
    colordic = config.colordic
    today = config.today
    velobit_ch_rnd = config.velobit_ch_rnd
    # existing = 0
    def __init__(self, tray, product, invert=0, loc = 0):
        super().__init__()
        # self.db = 'labview'
        # self.server = 'vl-mes-db01.velodyne.com'
        self.location = config.location[loc]
        self.dimensions_dict = config.dimensions_dict
        self.rows_dict = config.rows_dict
        self.inverted_list = config.inverted_list

        self.product = product
        self.tray_name = tray
        self.invert = invert

        self.db = pyodbc.connect('Driver={SQL Server};'
                                 'Server=%s;'
                                 'Database=%s;'
                                 'UID=%s;'
                                 'PWD=%s;'
                                 'Trusted_Connection=%s;'%(self.location['server'], self.location['db'], self.location['user'],self.location['pwd'], self.location['trusted']))

        if self.invert == 1:
            self.setStyleSheet("background-color: #241f1a;")
        else:
            self.setStyleSheet("background-color: #fff4e8;")
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.cursor = self.db.cursor()
        self.gui_build()

    def gui_build(self):
        #takes data from test_data
        self.test_data = self.test_data()[0]
        tableWidget = QTableWidget()
        for y in range(self.dimensions_dict[self.product][0]):
            for x in reversed(range(self.dimensions_dict[self.product][1])):
                self.index = [(self.dimensions_dict[self.product][1] * y + x + 1),(self.dimensions_dict[self.product][1] * y - x + self.dimensions_dict[self.product][1])]
                tableWidget.setItem(y, x, QTableWidgetItem(self.dimensions_dict[self.product][1] * y + x + 1))
                groupbox = QGroupBox()
                vbox = QVBoxLayout()
                groupbox.setLayout(vbox)
                groupbox.setStyleSheet("background-color: white")
                if self.test_data[self.index[self.invert] - 1] is not None:
                    sn = self.test_data[self.index[self.invert]-1].pop(0)
                    tray_place = self.index[self.invert]
                    bd_fail, message = self.get_breakdown_data(sn)
                    # comment = QPushButton("Add comment {SN}".format(SN=sn))
                    # comment.clicked.connect(lambda ch, Serial=sn: print(
                    #     "{SN} comment: ".format(SN=sn) + self.AddComment(sn)))
                    Breakdown = QPushButton(message)
                    Breakdown.clicked.connect(lambda ch, sn = sn: print(self.breakdown_test(sn)))
                    Breakdown.setStyleSheet(f"background-color: {config.breakdown_color[bd_fail]}")

                    label = QLabel("{SN}".format(SN=sn))
                    label_num = QLabel(str(self.index[self.invert]))
                    vbox.addWidget(label_num)
                    vbox.addWidget(label)
                    vbox.addWidget(Breakdown)
                    groupbox.setStyleSheet("background-color: lightblue")
                    labels = []
                    partial_tags = []
                    tags = []
                    bv = self.Bins[self.index[self.invert]-1]
                    for each in self.test_data[self.index[self.invert]-1]:
                        table = each[0].split('Testing')[1].split('_')[0]
                        final = each[0].split('Testing')[0][::-1].split('_')[0][::-1]
                        test = each[0].split('Testing')[1].split('_')[1]

                        tag = each[1]
                        partial_tags.append(tag.split(' ')[0])
                        tags.append(tag)
                        if final == 'Final':
                            table = final
                        if test == 'BootBiasCal':
                            table = 'BB'
                        tests = QLabel("{table}: {tag}".format(table = table, tag = tag))
                        labels.append(tests)
                        # print(partial_tags)
                        # print(tag)
                        tests.setStyleSheet("background-color: {color}".format(color=self.colordic[tag.split(' ')[0]]))

                        # print(table, tag)
                    if "Failed" in tags:
                        label.setStyleSheet("background-color: {color}".format(color=self.colordic["Failed"]))
                        groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Failed"]))
                        label.setText(sn + " ✘")
                    elif "Failing_Chs:" in partial_tags:
                        label.setStyleSheet("background-color: {color}".format(color=self.colordic["Failing_Chs:"]))
                        groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Failing_Chs:"]))
                        label.setText(sn + " *")
                    elif "Velobit" in tags:
                        label.setStyleSheet("background-color: {color}".format(color=self.colordic["Velobit"]))
                        groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Velobit"]))
                        label.setText(sn + " ℬ")
                    elif tags.count('Passed') == len(tags):
                        label.setStyleSheet("background-color: {color}".format(color=self.colordic["Passed"]))
                        label.setText(sn+" ✓")
                        groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Passed"]))
                    if bv == 'None' or bv is None:
                        pass
                    else:
                        bin = QLabel("Bin: {BV}".format(BV=bv))
                        bin.setStyleSheet("background-color: white")
                    for lab in labels:
                        vbox.addWidget(lab)
                    # vbox.addWidget(comment)

                    # label_num = QLabel(str(self.index))
                    label_num = QLabel(str(self.index[self.invert]))

                self.grid_layout.addWidget(groupbox, y, x)
                    # print(self.test_data[self.index[self.invert] - 1])

                    # bv = 2


                    # LD = QLabel("LD: {a}".format(a=ld))
                    # APD = QLabel("APD: {a}".format(a=apd))
                    # Final = QLabel("Final: {a}".format(a=fin))
                    # table.text.setStyleSheet("background-color: {color}".format(color=self.colordic[ld]))
                    # LD.setStyleSheet("background-color: {color}".format(color=self.colordic[ld.split(' ')[0]]))
                    #
                    # APD.setStyleSheet("background-color: {color}".format(color=self.colordic[apd.split(' ')[0]]))
                    # Final.setStyleSheet("background-color : {color}".format(color=self.colordic[fin.split(' ')[0]]))
                    # label.setStyleSheet("background-color: lightyellow")
                    # label.setStyleSheet("background-color: {color}".format(color=self.colordic["Passed"]))

                    # label_num = QLabel(str(self.index))

                    # if ld.split(' ')[0] == "Failed" or bb.split(' ')[0] == "Failed" or apd.split(' ')[0] == "Failed" or fin.split(' ')[0] == "Failed":
                    #     label.setStyleSheet("background-color: {color}".format(color=self.colordic["Failed"]))
                    #     groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Failed"]))
                    #     label.setText(sn + " ✘")
                    #
                    # elif ld.split(' ')[0] == "Failing_Chs:" or bb.split(' ')[0] == "Failing_Chs:" or apd.split(' ')[0] == "Failing_Chs:" or fin.split(' ')[0] == "Failing_Chs:":
                    #     label.setStyleSheet("background-color: {color}".format(color=self.colordic["Failing_Chs:"]))
                    #     groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Failing_Chs:"]))
                    #     label.setText(sn + " *")
                    # elif ld == "Velobit" or bb == "Velobit" or apd == "Velobit" or fin == "Velobit":
                    #     label.setStyleSheet("background-color: {color}".format(color=self.colordic["Velobit"]))
                    #     groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Velobit"]))
                    #     label.setText(sn + " ℬ")
                    # elif ld == "Passed" and bb == "Passed" and apd == "Passed" and fin == "Passed":
                    #     label.setStyleSheet("background-color: {color}".format(color=self.colordic["Passed"]))
                    #     label.setText(sn+" ✓")
                    #     groupbox.setStyleSheet("background-color: {color}".format(color=self.colordic["Passed"]))
                    # vbox.addWidget(label_num)


                    # vbox.addWidget(label)
                #     if bv == 'None' or bv is None:
                #         bv
                #     else:
                #         bin = QLabel("Bin: {BV}".format(BV=bv))
                #         bin.setStyleSheet("background-color: white")
                #         vbox.addWidget(bin)
                #     vbox.addWidget(LD)
                #     if self.product == 'TROSA_101':
                #         BB = QLabel("BB: {a}".format(a=bb))
                #         BB.setStyleSheet("background-color: {color}".format(color=self.colordic[bb]))
                #         vbox.addWidget(BB)
                #     vbox.addWidget(APD)
                #     vbox.addWidget(Final)
                #     vbox.addWidget(comment)
                # else:
                #     # label_num = QLabel(str(self.index))
                #     label_num = QLabel(str(self.index[self.invert]))
                #     vbox.addWidget(label_num)
                # self.grid_layout.addWidget(groupbox, y, x)
            self.button = QPushButton("New Tray")
            self.button.setStyleSheet('background-color: #d63c3c')
            self.flip_button = QPushButton("Flip tray (face down) ⮎")
            self.flip_button.setStyleSheet('background-color: #BC87CC;')
            self.refresh_button = QPushButton("Refresh {tray} (face up)".format(tray=self.tray_name))
            self.refresh_button.setStyleSheet('background-color: #56B064')
            self.UiComponents()
            self.grid_layout.addWidget(self.button)
            self.grid_layout.addWidget(self.refresh_button)
            self.grid_layout.addWidget(self.flip_button)
            self.setGeometry(50,50,500,600)
            # self.grid_layout.addWidget((self.send_email))
            self.setWindowTitle('TRAY {tray} {face}'.format(tray=self.tray_name, face=self.inverted_list[self.invert]))

    def get_breakdown_data(self, sn):
        bd_command = f'Select TOP {str(config.rows_dict[self.product])} cast(APD_breakdown_V as float) Breakdown, cast(Bin_Voltage as float) Bin, Channel, Temp_Compensated_V, Failed, FailureReason from labview.dbo.ApdBreakdown_CH Where SerialNumber = \'{sn}\' order by TStamp desc'
        bd_data = pd.read_sql(bd_command, self.db)
        bad_chs = ''
        for ch in bd_data[(bd_data['Failed'] == 1)]['Channel']:
            bad_chs = bad_chs + str(int(config.rows_dict[self.product])-int(ch)) + ' '
        if bd_data['Temp_Compensated_V'].dropna().empty is True and bd_data['Failed'].empty is False:
            bd_str = str(int(round(bd_data['Breakdown'].mean()))) + ' (No comp) '
        elif bd_data['Temp_Compensated_V'].dropna().empty is False and bd_data['Failed'].empty is False:
            bd_str = str(int(round(bd_data['Temp_Compensated_V'].mean())))
        if bd_data['Failed'].sum() == 0 and bd_data['Failed'].empty is False:
            if self.is_unique(bd_data['FailureReason']) == True:
                failed = 0
                display = 'Re-test Breakdown\nBD: ' + bd_str+'V'
            else:
                #failed = 3 is a warning of bin value off by 10V
                failed = 3
                display = 'Re-test Breakdown\nBD: ' + bd_str + 'V\n⚠:>10V off of Bin Voltage'
        elif bd_data['Failed'].sum() > 0 and bd_data['Breakdown'].max()-bd_data['Breakdown'].min() < 5:
            failed = 1
            display = 'Re-test Breakdown\nBD: ' + bd_str+'V'
        elif bd_data['Failed'].sum() > 0 and bd_data['Breakdown'].max()-bd_data['Breakdown'].min() > 5:
            failed = 1
            display = 'Re-test Breakdown\nCh fail: ' +bad_chs
        elif bd_data['Failed'].empty is True:
            #failed = 2 means not tested
            failed = 2
            display = f"Run Breakdown Test\nSN: {sn}"

        return failed, display

    def initUI(self):
        self.product = self.getProduct()
        self.tables = self.getTables(self.product)
        self.tray_name = self.getChoice()
        # return self.getTrayText()
        self.show()

    def is_unique(self, s):
        a = s.to_numpy()  # s.values (pandas<0.24)
        # print((a[0] == a).all())
        return (a[0] == a).all()

            # is_unique(df['counts'])

    # False

    def getTrayText(self):
        tray_number, okPressed = QInputDialog.getText(self, "Enter Tray Number", "Tray Number:", QLineEdit.Normal, "")
        if okPressed and tray_number != '':
            tray_command = "\'"+tray_number+"\'"
            return tray_command

    def AddComment(self, sn):
        #add a comment to a specific test result on some station.
        station, existing_comment = self.getColumn(sn)
        comment, okPressed = QInputDialog.getText(self, "{SN}".format(SN = sn), "{station} {SN}:".format(station = station, SN = sn), QLineEdit.Normal, existing_comment)
        if okPressed:
            #insert comment
            # insert_comment = 'SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;\nBEGIN TRANSACTION;\n' \
            #                  'UPDATE dbo.TROSA_tracker set {station} = \'{value}\' where SerialNumber = \'{SN}\' \nif @@ROWCOUNT = 0\nBEGIN\n\tInsert into [{db}].[dbo].[TROSA_tracker] (SerialNumber, {station}) values (\'{SN}\', \'{value}\')\nEND\nCOMMIT TRANSACTION'.format(station = station, value = comment, SN = sn, db= self.location['db'])

            insert_comment = 'SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;\nBEGIN TRANSACTION;\n' \
                             'UPDATE dbo.TROSA_tracker set {station} = \'{value}\' where SerialNumber = \'{SN}\' \nif @@ROWCOUNT = 0\nBEGIN\n\tInsert into [{db}].[dbo].[TROSA_tracker] (SerialNumber, {station}) values (\'{SN}\', \'{value}\')\nEND\nCOMMIT TRANSACTION'.format(
                station=station, value=comment, SN=sn, db = self.location['db'])
            self.cursor.execute(insert_comment)
            self.db.commit()
            return comment
        else:
            self.clickme_refresh()

    def breakdown_test(self, sn):
        # Run APD Breakdown test
        self.button.setStyleSheet('background-color: #FFC266')
        self.button.setText(f'{sn} Breakdown Test in Progress')
        # print("start")
        bin = self.getBin(sn)
        product = self.breakdown_prod(sn)
        # print(bin)
        try:
            APD.APD_breakdown(sn,bin,product).collect_each_ch()
            print("Test Finished")
        except:
            e = sys.exc_info()[0]
            print(traceback.format_exc())
            print("APD breakdown test run failure, please try again.", e)
        self.clickme_refresh()
    def breakdown_prod(self, sn):
        # print("Getting product")
        get_prod = f'Select ProductName from labview.dbo.SnStatus where SerialNumber = \'{sn}\''
        raw = self.cursor.execute(get_prod)
        for prod in raw:
            # print(prod)
            pass
        return prod[0]

    def getBin(self, sn):
        # print("Getting bin")
        get_bin = f'Select BinValue from labview.dbo.SnStatus where SerialNumber = \'{sn}\''
        raw = self.cursor.execute(get_bin)
        for bin in raw:
            # print(bin)
            pass
        return bin[0]


    def getColumn(self, sn):
        #used with AddComment, gets column names
        column_command = "Select COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'TROSA_tracker\' AND TABLE_SCHEMA = \'dbo\' AND COLUMN_NAME LIKE \'COMMENT%\' AND COLUMN_NAME NOT LIKE \'%QC\'"
        raw = self.cursor.execute(column_command)
        # print(sn)
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
            # print(select_existing)
            raw = self.cursor.execute(select_existing)
            # print("success")
            for row in raw:
                select_comment = str(row[0])

            return station, select_comment
        else:
            return station, ""

    def getProduct(self):
        #used with AddComment, gets column names
        get_prod = "Select ProductName from {db}.dbo.Products".format(db = self.location['db'])
        raw = self.cursor.execute(get_prod)
        # raw = pd.read_sql(column_command, self.db)
        # print("getting prod")
        prods = []
        for row in raw:
            prod = str(row[0])
            if prod:
                prods.append(prod)
                # print(prod)
            else:
                print("None")

        product,okPressed = QInputDialog.getItem(self, "Select Product","Products", prods, 0, False)
        if okPressed and product:
            return product

    def getChoice(self):
        recent_trays = 'SELECT Distinct TrayName FROM [{db}].[dbo].[SnStatus] where ProductName = \'{prod}\' order by TrayName desc'.format(prod = self.product, db=self.location['db'])
        # recent_trays = 'SELECT Distinct TOP (100) TrayName FROM [{db}].[dbo].[SnStatus]'
        raw = self.cursor.execute(recent_trays)
        tray_choice = ['Manually enter tray number']
        for row in raw:
            tray = str(row[0])
            if tray != "None" or tray is not None:
                tray_choice.append(tray)

        item, okPressed = QInputDialog.getItem(self, "Get Tray","Tray:", tray_choice, 0, False)
        if okPressed and item and item != 'Manually enter tray number':
            item = "\'"+item+"\'"
            return item
        elif okPressed and item == 'Manually enter tray number':
            return self.getTrayText()
    def test_data(self):
        #formerly init, pulls based on tray name input
        if self.tray_name is None:
            self.initUI()
            # self.tray_name = self.initUI()
        else:
            self.tables = self.getTables(self.product)
            # print(self.tray_name)
        # print(self.tray_name)
        self.grid = [None] * self.dimensions_dict[self.product][0]*self.dimensions_dict[self.product][1]
        # get_tray = 'Select SerialNumber, TrayPlace, BinValue from {db}.dbo.SnStatus Where TrayName = {tray_name} Order by TrayPlace'.format(
        #     tray_name=self.tray_name)
        get_tray = 'WITH most_recent AS (SELECT SerialNumber, TStamp, TrayName, TrayPlace, BinValue, ROW_NUMBER() OVER (PARTITION BY TrayPlace, TrayName ORDER BY TStamp DESC) AS rn FROM {db}.dbo.SnStatus AS s where ProductName = \'{product}\') Select SerialNumber, TrayPlace, BinValue from most_recent Where TrayName = {tray_name} and rn = 1 Order by TrayPlace'.format(tray_name=self.tray_name, db = self.location['db'], product = self.product)
        print(get_tray)

        self.Serials = []
        self.Bins = [None] * self.dimensions_dict[self.product][0]*self.dimensions_dict[self.product][1]
        #put serial numbers in tray location in grid.
        for row in self.cursor.execute(get_tray):
            self.Serials.append(row[0])
            self.Bins[int(row[1]) - 1] = row[2]
            self.grid[int(row[1]) - 1] = row[0]
        # print(self.get_sn_data(0))
        return self.get_sn_data(0)

    def pull_most_recent(self, table, columns, SN, use_today=0):
        #feeds into get_sn_data
        self.table = table
        self.columns = columns
        self.SN = SN
        self.use_today = self.today[use_today]
        self.most_recent = 'WITH most_recent AS (SELECT m.*, ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TestIndex DESC) AS rn \
                  FROM {db}.dbo.{table} as m) Select {columns} from most_recent WHERE rn <= {rows} and SerialNumber = {SN} {t} Order by TestIndex desc \
                '.format(table=self.table, columns=self.columns, SN=self.SN, t=self.use_today, rows = self.rows_dict[self.product], db= self.location['db'])
        # print(self.most_recent)
        raw = self.cursor.execute(self.most_recent)
        data = []
        for row in raw:
            fail = int(row[0])
            data.append(fail)
        chs = ''
        if sum(data) == 0 and len(data) > 0:
            tag = "Passed"
        # elif sum(data) != 0 and data[int(self.velobit_ch_rnd - 1)] == 0:
            # tag = "Velobit (Passed Ch{ch})".format(ch = self.velobit_ch_rnd)
            # tag = "Velobit"
            # (Passed Ch{ch})".format(ch=self.velobit_ch_rnd)
        elif len(data) == 0:
            tag = "Untested"
        else:
            for n,i in enumerate(data):
                if i == 1:
                    # chs = chs+' '+str(len(data)-n)
                    chs = chs + ' ' + str(n+1)
                elif i == 0:
                    chs = chs +' '+ '✓'
            if sum(data) == len(data):
                tag = "Failed"
            else:
                tag = "Failing_Chs:"+chs
        return data, tag

    # def get_sn_data(self, today=0):
    #     #gets all SNs in single tray, gets data.
    #     for SN in self.grid:
    #         if SN is not None:
    #             self.LP, self.tlp = self.pull_most_recent('{prod}_InitialTestingLD_AsicLpTest_CH'.format(prod=self.product), 'Failed',
    #                                                       '\'{SN}\''.format(SN=SN),today)
    #             self.APD, self.tapd = self.pull_most_recent('{prod}_InitialTestingAPD_ApdLifeTest_CH'.format(prod=self.product), 'Failed',
    #                                                         '\'{SN}\''.format(SN=SN),today)
    #             self.BB, self.tbb = self.pull_most_recent('{prod}_InitialTestingLD_BootBiasCal_CH'.format(prod=self.product), 'Failed',
    #                                                       '\'{SN}\''.format(SN=SN),today)
    #             self.F, self.tf = self.pull_most_recent('{prod}_FinalTestingLD_FinalTestLD_CH'.format(prod=self.product), 'Failed',
    #                                                     '\'{SN}\''.format(SN=SN),today)
    #             self.grid[self.grid.index(SN)] = [SN, self.tlp, self.tbb, self.tapd, self.tf, self.Bins[self.grid.index(SN)]]
    #     return self.grid, self.tray_name

    def getTables(self, product):
        #take all CH table that this database has for this product,input the product
        tables = 'select top 4 name from sysobjects where xtype = \'U\' and right(name,2) = \'CH\' and left(name,len(\'{product}\')) = \'{product}\' order by crdate'.format(db = self.location['db'], product = product)
        # print(tables)
        raw = self.cursor.execute(tables)
        test_order = ['LD_AsicLpTest_CH', 'LD_BootBiasCal_CH', 'APD_ApdLifeTest_CH', 'LD_FinalTestLD_CH']
        tests = []
        test_order = []

        # print(len(raw))
        for test in raw:
            tests.append(test)
            test_order.append(str(test).split('Testing')[1])
        return tests
        # test_order = ['LD_AsicLpTest_CH','LD_BootBiasCal_CH','APD_ApdLifeTest_CH','LD_FinalTestLD_CH']

    def get_sn_data(self, today=0):
        # gets all SNs in single tray, gets data.
        for n, SN in enumerate(self.grid):
            if SN is not None:
                self.grid[n] = [SN]
                # print(self.grid)
                for table in self.tables:
                    data, tag = self.pull_most_recent(table[0], 'Failed',
                                                      '\'{SN}\''.format(SN=SN), today)
                    self.grid[n].append([table[0], tag])
                    # print(type(self.grid[self.grid.index([SN])]))

                # self.grid[self.grid.index(SN)] = [SN, self.tlp, self.tbb, self.tapd, self.tf]
                # print('GRID: ', self.grid)
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
        self.button.clicked.connect(self.clickme_new_tray)
        self.refresh_button.clicked.connect(self.clickme_refresh)

        self.flip_button.clicked.connect(self.clickme_flip)
        # self.send_email.clicked.connect(self.clickme_send_email)

    def clickme_new_tray(self):
        self.button.setStyleSheet('background-color: yellow')
        self.button.setText('Enter New Tray')
        self.New = basicWindow(None,None)
        self.New.show()
        self.close()

    def clickme_refresh(self):
        self.refresh_button.setStyleSheet('background-color: yellow')
        self.refresh_button.setText('Refreshing')
        self.New = basicWindow(self.tray_name,self.product)
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
    def clickme_flip(self):
        self.flip_button.setStyleSheet('background-color: yellow')
        self.flip_button.setText('Flipping tray')
        self.New = basicWindow(self.tray_name,self.product,invert=1)
        self.New.show()
        self.close()

if __name__ == '__main__':

    windows = []
    refresh = 0
    app = QApplication(sys.argv)
    windows.append(basicWindow(None,None))
    windows[refresh].show()
    sys.exit(app.exec_())
