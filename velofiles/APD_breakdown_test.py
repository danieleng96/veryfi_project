import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import config
# import APD_breakdown.Omega_Platinum as temp
import SourceMeter as source
import DAQ970A as daq
import SQL_server as sql_server
# import TC_720 as temp
import PyQt5
from PyQt5.QtGui import *
import sys
from PyQt5 import QtGui

# import seaborn as sns

from PyQt5.QtWidgets import (QPushButton,
                              QVBoxLayout, QTableWidgetItem, QTableWidget, QHeaderView, QWidget, QMainWindow)
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class TableWidget(QTableWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.setStyleSheet('font-size: 15px;')
        self.setStyleSheet('font-size: 30px;')


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
class Graph_Table(QWidget):
    def __init__(self, df, vrange, parent):
        super().__init__(parent=parent)
        if df.empty is False:

            self.resize(1000, 500)
            self.resize(2000, 800)
            self.parent = parent
            self.df = df
            sn = self.df.iloc[0].SerialNumber
            self.df = self.df.loc[:, self.df.columns != 'SerialNumber']
            # self.db = db
            # self.cursor = cursor
            # self.tray = str(self.df.loc[0,'TrayName'])
            # self.product = str(self.df.loc[0,'ProductName'])
            # from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            #
            # self.figure = plt.figure()
            # self.canvas = FigureCanvas(self.figure)

            # plot barplot, MplCanvas
            import matplotlib.patches as mpatches

            sc = MplCanvas(self, width=5, height=4, dpi=100)

            labels = [f'Ch{ch}' for ch in df['Channel']]
            breakdown_raw = abs(df['APD_breakdown_V'])
            temp_breakdown = abs(df['Temp_Compensated_V'])
            temp_breakdown_p = abs(df[df['Failed']== 0]['Temp_Compensated_V'])
            temp_breakdown_f = abs(df[df['Failed']== 1]['Temp_Compensated_V'])
            #add lims based on data
            max = breakdown_raw.max()
            min = temp_breakdown.min()-1
            if min > 100:
                min = min-1
            max = max+1
            sc.axes.set_ylim(min,max)
            diff = round(breakdown_raw - temp_breakdown, 2)
            width = 0.35  # the width of the bars: can also be len(x) sequence
            # sc.axes.scatter(df['Channel'], breakdown_raw, label = 'Raw V')
            # sc.axes.bar(labels, breakdown_raw, width, label='Temp Adjusted V')
            # for n, c in enumerate(df['Channel']):
            #     arrow = mpatches.FancyArrowPatch((c, breakdown_raw[n]), (c, temp_breakdown[n]),
            #                                  mutation_scale=100)
            #     sc.axes.add_patch(arrow)
            # sc.axes.bar(labels, diff, width, bottom=temp_breakdown,
            #             label='Temperature Adjust', alpha = .5)


            # plt.show()
            # mainLayout = QVBoxLayout()
            mainLayout = QVBoxLayout()
            self.table = TableWidget(self.df.round(2))
            self.table.setStyleSheet('font-size: 8px; font-weight:bold; border: 1px solid black; background: lightgreen')
            self.table.setStyleSheet('font-size: 16px; font-weight:bold; border: 2px solid black; background: lightgreen')
            point_cols = []
            for i in range(self.df.shape[0]):
                if int(self.df.iloc[i]['Failed']) == 1:
                    for j in range(self.df.shape[1]):
                        self.table.item(i, j).setBackground(QtGui.QColor(248, 117, 117))
            f = df[df['Failed'] == 1]
            if f.empty is False:
                sc.axes.plot(f['Channel'].astype(int), temp_breakdown_f, label = 'Failed Adjusted V', marker = '^', markersize = 17, color = '#a63933', linestyle = '')
                # for n,each in enumerate(f.iterrows()):
                    # print('name',each['Temp_Compensated_V'])
                    # sc.axes.annotate(text = each['FailureReason'], (each['Channel'].astype(int),each['Temp_Compensated_V'].astype(int)))
            sc.axes.plot(df[df['Failed']==0]['Channel'].astype(int), temp_breakdown_p, label = 'Adjusted V', marker = '^', markersize= 15, color = 'white', linestyle = '')
            sc.axes.plot(df['Channel'].astype(int), breakdown_raw, label = 'Raw V', marker = 'v', markersize = 15, linestyle = '', color = 'yellow')
            # sc.axes.fill(x = [-1,9], y=abs(vrange), color = 'b', alpha = 0.5)
            # print(vrange)

            sc.axes.set_ylabel('Breakdown Voltage')
            sc.axes.set_xlabel('Channel')
            sc.axes.set_title(f'Breakdown Voltage by Channel\nSerial = {sn}')
            sc.axes.set_facecolor(color = 'lightblue')
            sc.axes.grid(which = 'major', axis = 'both')
            x = np.array([0,7])


            sc.axes.fill_between(x,abs(vrange[1]),abs(vrange[0]),color = 'yellow', alpha = 0.5)
            sc.axes.legend()

            self.setWindowFlag(Qt.FramelessWindowHint)
            mainLayout.addWidget(sc)
            mainLayout.addWidget(self.table)

            # self.setCentralWidget(self.table)
            # button_print = QPushButton('Open Full tray')
            # button_print.setStyleSheet('font-size: 10px; font-weight:bold; border-style: solid; border-radius:15px; border: 3px solid black; background: #70ade6')

            # button_print.setStyleSheet('font-size: 15px')
            # button_print.clicked.connect(self.display_table)
            # mainLayout.addWidget(button_print)

            button_close = QPushButton('Complete test')
            button_close.setStyleSheet('font-weight: bold; font-size: 15px')
            button_close.clicked.connect(self.close_button)
            mainLayout.addWidget(button_close)
            # mainLayout.addWidget(self.canvas)

            # print('SN Search')
            self.setLayout(mainLayout)

    def close_button(self):
        self.parent.close()

class DFEditor(QMainWindow):

    def __init__(self, df, vrange):
        super().__init__()
        self.w = None
        self.setCentralWidget(Graph_Table(df, vrange, parent = self))
        #add to show
        # self.showMaximized()
        # print(self.tray, self.product, self.db, self.cursor)
        # self.show()


    # def plot(self,df):
    #     # ax = sns.barplot(x="Channel", y="Temp_Compensated_V", hue="Failed", data=df)
    #
    #     # import matplotlib.pyplot as plt
    #
    #
    #     # clearing old figure
    #     self.figure.clear()
    #
    #     # create an axis
    #     ax = self.figure.add_subplot(111)
    #
    #     # plot data
    #     ax.plot(df, '*-')
    #
    #     # refresh canvas
    #     self.canvas.draw()
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        matplotlib.use('Qt5Agg')

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


# class MainWindow(QtWidgets.QMainWindow):
#
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#
#         # Create the maptlotlib FigureCanvas object,
#         # which defines a single set of axes as self.axes.
#         sc = MplCanvas(self, width=5, height=4, dpi=100)
#         sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
#         self.setCentralWidget(sc)
#
#         self.show()
#add in range finding, run a
class APD_breakdown:
    def __init__(self, sn, bin = None, product = 'APA'):
        self.product = product
        self.sn = sn
        self.bin = bin
        self.dq = daq.DAQ970A()
        self.sm = source.Keithley_2400()
        # self.temp = temp.TC720()
       # ## # self.temp = temp.Omega_Platinum()
        self.sql = sql_server.py_sql()
    def range_finding_sweep(self, c):
        print('Range finding')
        # print(self.temp.get_temp())
        self.dq.close_channels(self.dq.channels[c])
        self.sm.pre_sweep()
        buff = self.sm.run_sweep()
        dec_data, df, breakdown, leak, std = self.sm.breakdown_processing(buff)
        # print(dec_data)
        # if abs(float(breakdown)) > 110 and abs(float(breakdown)) < 210:
        range_start = round(breakdown + 5)
        range_end = round(breakdown - 5)
        # else:
        #     # range_start, range_end = self.range_finding_sweep()
        #     range_start = -210
        #     range_end = -130
        return range_start, range_end

    def set_manual_reading(self, chan = 3, voltage = -170):
        self.dq.open_channels(self.dq.channel_str)
        time.sleep(1)
        self.dq.close_channels(self.dq.channel_str)
        mode = 'VOLT'
        sense = 'CURR'
        self.sm.dev.write("SENS:FUNC:CONC OFF")
        self.sm.dev.write(f"SOUR:FUNC {mode}")
        self.sm.dev.write(f"SENS:FUNC '{sense}:DC'")
        self.sm.dev.write("SENS:CURR:PROT 3e-6")
        self.sm.dev.write(f"SOUR:MODE:FIXED")

        self.sm.dev.write(f"SOUR:VOLT:LEV {voltage}")
        self.sm.dev.write("OUTP ON")
        for i in range(5):
            if i == 0:
                print(i)
                self.sm.dev.write(f"TRIG:COUN 5")
                # time.sleep(2)
                print(self.sm.dev.query('READ?'))
                data = self.sm.dev.query('FETC?')

                print(data, type(data))
                i+=1
                time.sleep(10)
            elif i > 0:
                self.sm.dev.write(f"TRIG:COUN 5")
                time.sleep(2)
                data += self.sm.dev.query('FETC?')

                print(data, time.localtime())
                time.sleep(20)
                i+=1

    def collect_each_ch(self):
        # self.sql.pull_total_data()
        print(f"Breakdown for SN {self.sn}")
        t0 = time.time()
        labels = ["SerialNumber", "Channel", "ProductName", "APD_breakdown_V", "Ch_Duration", "Failed", "Bin_Voltage", "Avg_Leak_Current", "STD_Leak_Current", "Temp", "Temp_Compensated_V", "FailureReason"]
        all_ch_data = []
        colors = ['k', 'b', 'orange', 'r', 'teal', 'purple', 'lime', 'yellow']
        #open_all
        legend = []
        breakdowns = []
        self.dq.open_channels(self.dq.channel_str)
        #make own command to run this sweep, -160 to -210
        # for ch in range(config.prod_ch[self.product])

        for ch in range(config.prod_ch[self.product]):
            range_start, range_end = self.range_finding_sweep(ch)
            #DANIEL CHANGES
            # range_start, range_end = -140, -210

            if (abs(float(range_start)) > 110 and abs(float(range_end)) < 230):
                break
            elif ch == config.prod_ch[self.product] and not (abs(float(range_start)) > 110 and abs(float(range_end)) < 230):
                print("All channels failed, setting wider range")
                range_start = -130
                range_end = -230
            else:
                print(f'Need to continue scan, scanning Ch{ch}')

        # range_start = -180
        # range_end = -190
        # fig, ax1, ax2 = plt.subplots(2)
        leak_curr = []
        leak_curr_std = []
        comp_breakdowns = []

        for ch in range(config.prod_ch[self.product]):

            t0_ch = time.time()
            print(f"Channel: {ch}")
            print(f"channel {self.dq.channels[ch]}")
            self.dq.close_channels(self.dq.channels[ch])
            time.sleep(1)
            self.sm.set_IV_curve_sweep(start = range_start, end = range_end)
            buff = self.sm.run_sweep()
            dec_data, df, breakdown, avg_leak, std_leak = self.sm.breakdown_processing(buff)
            # print(df)
            # temperature = self.temp.get_temp()
            temperature = 22

            print('Temperature: '+ str(temperature)+'C')
            #get temp for each channel
            failed,bin_breakdown,FailureReason = self.compare_bins(breakdown)

            breakdowns.append(breakdown)

            comp_t_v, high_t_v, low_t_v = self.temp_comp(breakdown,temperature)
            print("difference between bin value and BD test: " + str(abs(bin_breakdown - comp_t_v)))
            plot_curr = df['curr'].apply(lambda x: x*(1e6))
            # plt.plot(df['volt'], plot_curr, color = colors[ch])
            # plt.plot(df['volt'].apply(lambda x: x-(float(temperature)-22)*config.volts_degree_c), plot_curr, colors[ch])
            comp_breakdowns.append(comp_t_v)
            # legend.append(f"Channel {ch}")
            # plt.xlabel('Voltage (V) (Compensated to 22C)', fontweight = 'bold')
            # plt.ylabel('Current (μA)', fontweight = 'bold')
            t = str(round(time.time()-t0_ch))
            print(f"Channel {ch} time: {t}")
            ch_data = [self.sn, ch, self.product, breakdown, t, failed, bin_breakdown, avg_leak, std_leak, temperature, comp_t_v, FailureReason]
            all_ch_data.append(ch_data)
            self.dq.open_channels(self.dq.channel_str)
            time.sleep(1)
            leak_curr.append(avg_leak)
            leak_curr_std.append(std_leak)
        # ax2.errorbar(data_ch['Channel'], data_ch['AVG_TROSA'], yerr=data_ch['STDEV_TROSA'], marker='o', color = 'red', linestyle='None')
        # ax2.set_xlabel('Channel', fontweight='bold')
        # ax2.set_ylabel('Current (μA)', fontweight='bold')



        # ax = plt.axes()
        # ax.set_facecolor("#BBB0FF")
        # fig = plt.gcf()
        # fig.canvas.set_window_title('APD Breakdown Test')
            #plot bin range
        bin_string = ""
        average_breakdown = round(sum(breakdowns) / len(breakdowns),2)
        average_comp_breakdown = round(sum(comp_breakdowns) / len(comp_breakdowns), 2)
        if self.bin:
            if self.bin >= 30:
                bin_breakdown = -(self.bin * 5 + 12.5)
            elif self.bin < 30:
                bin_breakdown = -(self.bin + 180)
        else:
            bin_breakdown = 0
        # plt.axvspan(-(bin_breakdown+1), -(bin_breakdown-1), color = '#EED4FF', alpha = 0.5)
        # plt.text(-(bin_breakdown+1), -3, f"2V Bin", size=10)
        bin_string = f"\nBin Voltage {-(bin_breakdown)} to {-(bin_breakdown+1)} V"
        # plt.title(f"SN: {self.sn} \n Breakdown IV  Curve", fontweight = 'bold')
        print("Total Time (s): "+ str(time.time()-t0))
        # plt.legend(legend)

        print(average_breakdown)
        # plt.text(min(comp_breakdowns)+2.5, -1, f"Tested Breakdown {average_breakdown} V\nTemp Compensated Breakdown {average_comp_breakdown} V{bin_string}", size=10, ha="center", va="center",
        #  bbox=dict(boxstyle="round",
        #            ec='k',
        #            fc='#CFF5FF',
        #            )
        #  )
        # plt.hlines(y=2e-6, max = -190, min = -200, color='orange', linestyle='dotted')
        # for ch, bd in enumerate(breakdowns):
            # plt.axvline(x = bd, color = colors[ch], linestyle = 'dashed', alpha = 0.2)
            # plt.axvline(x = comp_breakdowns[ch], color = colors[ch], linestyle = 'dashed')

        # plt.axvline()
        # plt.axhline(y = -2, linestyle = 'dotted', color = 'white')
        data_df = pd.DataFrame(all_ch_data, columns = labels)
        #dummy data
        # data_df = pd.read_excel('sample_bd.xlsx')
        spread, vrange, data_df = self.Spread(data_df)
        # spread, data_df = self.maxDiff(comp_breakdowns, data_df)
        data_df = data_df.sort_values(by = "Channel")
        print(data_df)
        display_labels = ["SerialNumber", "Channel", "ProductName", "Temp_Compensated_V", "APD_breakdown_V",  "Bin_Voltage", "Temp", "Failed", "FailureReason"]
        display = data_df[display_labels]
        self.sql.enter_data(data_df)
        app = PyQt5.QtWidgets.QApplication(sys.argv)
        w = DFEditor(display, vrange)
        # DFEditor(data_df)
        w.show()
        app.exec_()




    # def maxDiff(self, bd, data_df):
    #     vmin = bd[0]
    #     dmax = 0
    #     for i in range(len(bd)):
    #         if (bd[i] < vmin):
    #             vmin = bd[i]
    #         elif (bd[i] - vmin > dmax):
    #             dmax = bd[i] - vmin
    #     if dmax > 5:
    #         trosa_failed = 1
    #         data_df = data_df.assign(Failed=trosa_failed)
    #         failure_reason = 'Ch_Spread>5V'
    #         data_df['FailureReason'][(data_df['FailureReason'] != '')] = data_df['FailureReason'][(data_df['FailureReason'] != '')].astype(str) + ',' + failure_reason
    #         data_df['FailureReason'][(data_df['FailureReason']== '')] = data_df['FailureReason'][(data_df['FailureReason']== '')].astype(str)+failure_reason
    #     return dmax, data_df
    def Spread(self, data_df):
        # print("running")
        data_df = data_df.sort_values(by='Temp_Compensated_V')
        bd = pd.to_numeric(data_df['Temp_Compensated_V'], errors = 'coerce')
        print(bd)
        # print(data_df)
        # deltas = [0]
        def MaxDiff(bd):
            dmax = 0
            vmin = bd.iloc[0]
            vmax = bd.iloc[0]
            for i in range(len(bd)):
                if (bd.iloc[i] < vmin):
                    vmin = bd.iloc[i]
                elif (bd.iloc[i] > vmax):
                    vmax = bd.iloc[i]
                elif (bd.iloc[i] - vmin > dmax):
                    # ind.append(i)
                    dmax = bd.iloc[i] - vmin
            dmax = vmax - vmin
            return dmax, [vmin, vmax]

        ind = [0]
        dmax, vrange = MaxDiff(bd)
        print('dmax',dmax)
        if dmax > 5:
            new_sum = 0
            deltas = [0]
            for i in range((len(bd)) - 1):
                delt = (bd.iloc[i + 1] - bd.iloc[i])
                deltas.append(delt)
                new_sum = new_sum + delt
                if new_sum > 5:
                    new_sum = 0
                    ind.append(i + 1)
            # print(deltas)
            ind.append(len(bd))
            length = 0
            span = 0
            for n in range(len(ind) - 1):
                slice = bd.iloc[ind[n]:ind[n + 1]]
                length_each = len(slice)
                if length_each > length:
                    main_slice = slice
                    length = length_each
                elif length_each == length:
                    if span > MaxDiff(slice):
                        main_slice = slice
                        length = length_each
                    else:
                        length = length_each
                else:
                    length = length_each
                span = MaxDiff(slice)
            # print(span)
            data_df = data_df.assign(Failed=1)

            for each in main_slice.index:
                data_df.at[each, 'Failed'] = 0
            data_df = data_df.sort_index()

            failure_reason = 'Ch_Spread>5V'
            data_df['FailureReason'][(data_df['FailureReason'] != '')] = data_df['FailureReason'][
                                                                             (data_df['FailureReason'] != '')].astype(
                str) + ',' + failure_reason
            data_df['FailureReason'][(data_df['FailureReason'] == '')] = data_df['FailureReason'][
                                                                             (data_df['FailureReason'] == '')].astype(
                str) + failure_reason
        return dmax, vrange, data_df

    def temp_comp(self, breakdown, temperature):
        # temp_bin_high = -(self.bin+180) + (self.temp-22)*(config.volts_degree_c +config.vpd_error)
        # temp_bin_low = -(self.bin+180) + (self.temp-22)*(config.volts_degree_c - config.vpd_error)
        volt_22_high = breakdown - (temperature-22)*(config.volts_degree_c + config.vpd_error)
        if abs(breakdown) < 10:
            volt_22 = 0
        else:
            volt_22 = breakdown - (temperature-22)*config.volts_degree_c
        volt_22_low = breakdown - (temperature-22)*(config.volts_degree_c - config.vpd_error)
        return volt_22, volt_22_high, volt_22_low

    def compare_bins(self, bd):
        if self.bin:
            if self.bin >= 30:
                bin_breakdown = -(self.bin*5 +12.5)
            elif self.bin < 30:
                bin_breakdown = -(self.bin + 180)
            bd_delta = abs(bin_breakdown - bd)
            if bd_delta > 10:
                print("Out of spec")
                if abs(bd) < 100:
                    print("Out of spec")
                    fail_reason = 'Non_convergent_low'
                    failed = 1
                elif abs(bd) > 230:
                    print("Out of spec")
                    fail_reason = 'Non_convergent_high'
                    failed = 1
                else:
                    failed = 0
                    fail_reason = '>10V_out_of_Bin'
            else:
                failed = 0
                fail_reason = ''
                print("Good channel")
            return failed, bin_breakdown, fail_reason
        else:
            return 0, 0, ''

    def sample_plot(self, file):
        data_df = pd.read_csv(file)
        spread, vrange, data_df = self.Spread(data_df)
        # spread, data_df = self.maxDiff(comp_breakdowns, data_df)
        data_df = data_df.sort_values(by = "Channel")
        print(data_df)
        display_labels = ["SerialNumber", "Channel", "Temp_Compensated_V", "APD_breakdown_V",  "Bin_Voltage", "Temp", "Failed", "FailureReason"]
        display = data_df[display_labels]
        # self.sql.enter_data(data_df)
        app = PyQt5.QtWidgets.QApplication(sys.argv)
        w = DFEditor(display, vrange)
        app.exec_()

if __name__ == '__main__':
    s = source.Keithley_2400()
    # for i in range(5):
        #change sn = " " and write the serial number that you want to test here.
    APD_breakdown(sn = "b1g1_test", product = 'TROSA_101').collect_each_ch()
    # a.Spread(pd.read_csv('sample_bd_fail.csv'))
    # a.sample_plot('sample_bd_fail.csv')
    # a.sample_plot('sample_bd.csv')
    # s.TROSA_classic_positive_negative(f'B056_verif')