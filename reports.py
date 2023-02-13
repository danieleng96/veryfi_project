import pyodbc
import numpy as np
from flask import Flask
import pandas as pd
from IPython.core.display import display, HTML
import sys
import matplotlib.pyplot as plt
import seaborn as sns
#import flask
#things happen on server, things are visually displayed.
class DailyReport:
    def __init__(self):
        self.db = pyodbc.connect('Driver={SQL Server};'
                                 'Server=vl-mes-db01.velodyne.com;'
                                 'Database=labview;'
                                 'Trusted_Connection=yes;')
        self.SNs = []
        self.cursor = self.db.cursor()
        self.velobit_ch_rnd = 5
        self.table_to_comment_dic = {'TROSA_101_InitialTestingLD_AsicLpTest_CH':'CommentInitialLD','TROSA_101_InitialTestingLD_BootBiasCal_CH':'CommentInitialLD','TROSA_101_InitialTestingAPD_ApdLifeTest_CH':'CommentAPD','TROSA_101_FinalTestingLD_FinalTestLD_CH':'CommentFinalTesting'}
        # pulling all data from today.
    def pull_today_data(self, table, days_back = 0):
        self.days_back = days_back
        # feeds into get_sn_data
        passed = 0
        velobit = 0
        failed = 0
        self.table = table
        # data_dic = {}
        sns = []
        full_comment = ''
        get_sns = 'Select Distinct SerialNumber from labview.dbo.{table}\nWHERE convert(varchar(10), TStamp, 102) = \'{date}\''.format(table=self.table, date = self.date)
        sn_list_command = self.cursor.execute(get_sns)
        for i, sn in enumerate(sn_list_command):
            sns.append(sn[0])
            # print(sn[0])
        # print("Total:", i+1, self.table)
        for sn in sns:
            self.most_recent = 'WITH most_recent AS (SELECT m.*, ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TestIndex DESC) AS rn '\
        'FROM dbo.{table} m) Select SerialNumber, Failed from most_recent WHERE rn < 9  and SerialNumber = \'{sn}\' and convert(varchar(10), TStamp, 102) = \'{date}\' Order by TestIndex desc'.format(sn=sn, table=self.table, date=self.date)
            # print(self.most_recent)
            raw = self.cursor.execute(self.most_recent)
            data = []
            for row in raw:
                self.SNs.append(row[0])
                fail = int(row[1])
                data.append(fail)
                self.SNs = (list(set(self.SNs)))
            if sum(data) == 0 and len(data) > 0:
                tag = "Passed"
                passed += 1
                # print(passed)
            elif sum(data) != 0 and data[int(self.velobit_ch_rnd - 1)] == 0:
                # tag = "Velobit (Passed Ch{ch})".format(ch = self.velobit_ch_rnd)
                tag = "Velobit"
                velobit += 1
                # (Passed Ch{ch})".format(ch=self.velobit_ch_rnd)
            elif len(data) == 0:
                tag = "Untested"
            else:
                tag = "Failed"
                failed += 1
            comment = self.get_comment(sn, self.table)
            tag = [tag, comment]
            # data_dic[sn] = tag
            if comment and comment != "":
                comment = sn + " : " + comment
                full_comment = (full_comment + comment + " ").strip()
            else:
                full_comment = ""
        # breakdown = [passed,failed,velobit,full_comment]
        breakdown = [passed, failed, velobit]
        # breakdown_list = [passed,failed,velobit,full_comment]
        return  breakdown
    #data_dic = list of dictionaries, each index is a different table. Each SN in each
    def get_comment(self, sn, table):
        comment_column = self.table_to_comment_dic[table]
        command = "Select {comment_column} from labview.dbo.TROSA_tracker where SerialNumber = \'{sn}\'".format(comment_column=comment_column, sn=sn)
        raw = self.cursor.execute(command)
        comment = ""
        for row in raw:
            comment = row[0]
        return comment

    def get_all_today(self, days_back = 0):
        command_date = "Select convert(varchar(10), DATEADD(day, -{days_back}, getdate()), 102)".format(days_back=str(days_back))
        raw = self.cursor.execute(command_date)
        for date in raw:
            continue
        self.date= date[0]
        # gets all SNs in single tray, gets data.
        # self.LP, self.tlp = self.pull_today_data('TROSA_101_InitialTestingLD_AsicLpTest_CH')
        self.APD  = self.pull_today_data('TROSA_101_InitialTestingAPD_ApdLifeTest_CH', days_back)
        self.BB = self.pull_today_data('TROSA_101_InitialTestingLD_BootBiasCal_CH', days_back)
        self.F = self.pull_today_data('TROSA_101_FinalTestingLD_FinalTestLD_CH', days_back)
        # self.grid=[self.tbb, self.tapd, self.tf]
        self.grid_data = (self.BB,self.APD,self.F)
        # self.grid_data = pd.DataFrame([self.BB,self.APD,self.F], columns = ["Pass","Fail","Velobit","Comment"], index = ['Initial LD','Initial APD', 'Final LD'])
        self.grid_data = pd.DataFrame([self.BB,self.APD,self.F], columns = ["Pass","Fail","Velobit"], index = ['Initial LD','Initial APD', 'Final LD'])
        # self.grid_data = pd.DataFrame([self.BB, self.APD, self.F], columns=["Pass", "Fail", "Velobit"])

        # self.grid_data = [self.BB,self.APD,self.F]
        # self.grid_data.style.set_caption(str(self.date))
        # self.grid_data.style.set_caption(str(self.date))
        return self.grid_data, self.date

report = DailyReport()
date = []
array = []
total_frame = pd.DataFrame()
# fig = plt.figure()
# ax = fig.add_subplot(111)
for i in range(3):
    a, d = report.get_all_today(days_back=i)
    # print(a.loc['Initial LD'])
    # a.loc['Initial APD'].plot(kind = "bar")
    # f = a.loc['Final LD']
    # ld = a.loc['Initial LD']
    # apd = a.loc['Initial APD']
    # ax.plot(ld)
    # a.loc['Final LD']
    array.append(a)
    date.append(d)
# plt.show(
# cmap = cmap=sns.diverging_palette(27,61, as_cmap=True)
# def magnify():
#     return [dict(selector="th",
#                  props=[("font-size", "10pt")]),
#             dict(selector="td",
#                  props=[('padding', "0em 0em")]),
#             dict(selector="th:hover",
#                  props=[("font-size", "20pt")]),
#             dict(selector="tr:hover td:hover",
#                  props=[('max-width', '200px'),
#                         ('font-size', '20pt')])]
def hover(hover_color="#ffff99"):
    return dict(selector="tr:hover",
                props=[("background-color", "%s" % hover_color)])

def highlight_LD(x):
    return ['background-color: lightblue' if s % 3 == 0 else ''
            for s in range(len(x))]

def highlight_APD(x):
    return ['background-color: lightgreen' if s % 3 == 1 else ''
            for s in range(len(x))]

def highlight_F(x):
    return ['background-color: lavender' if s % 3 == 2 else ''
            for s in range(len(x))]
    # if e == 0:
    #     color = 'white'
    #     return 'background-color: {color}'.format(color=color)
total_frame = pd.concat(array, keys = date)
# total_frame = pd.concat(array)
# total_frame = total_frame.reset_index()
# total_frame.rename(columns = {'level_0':'Date','level_1':'Test'})
# print(total_frame.iloc[1])
# print(total_frame)
# print(total_frame.style\
#         .background_gradient(cmap, axis=1) \
#         .set_properties(**{'max-width': '160px', 'font-size': '10pt'}) \
#         # .set_table_styles(magnify())
#         .render())
# print(total_frame)
# making a green border

styles = [
    hover(),
    dict(selector="th", props=[("font-size", "100%"),
                               ("text-align", "center")])
]
html = (total_frame.style\
        .set_table_styles(styles)\
        .apply(highlight_LD, axis = 0)\
        .apply(highlight_APD, axis = 0)\
        .apply(highlight_F, axis = 0)\
        .highlight_min(color = 'white')\
        .set_table_styles([{'selector': 'th', 'props': [('font-size', '12pt'),('border-style','solid'),('border-width','1px')]}])\
        .set_table_styles([{'selector' : '',
                            'props' : [('border',
                                        '2px solid green')]}]))
ht = html.render()

app = Flask(__name__)

@app.route("/")
def home():
    return ht

if __name__ == "__main__":
    app.run()
# f = open("display_report.html", "r+")
# print(f.read())
# f.truncate(0)
# f.close()
# with open('display_report.html','w') as writer:
#     writer.write(ht)

# cm = sns.light_palette("green", as_cmap = True)
# total_frame.apply(pd.to_numeric).style.background_gradient(cmap = cm)
# array.plot(kind = "bar")
# plt.legend(loc="best")
# plt.show()
# display(total_frame)

# date = np.array(date)
# array.append(a)
# print(array,date)
# df = pd.DataFrame(data = date.T, columns =pd.MultiIndex.from_tuples())



# # model = DataFrameModel(df = report.get_all_today())
# app=QtWidgets.QApplication(sys.argv)
# window=MainWindow(report.get_all_today())
# window.show()
# app.exec_()

# if __name__ == '__main__':
#
#     windows = []
#     refresh = 0
#     app = QApplication(sys.argv)
#     windows.append(basicWindow(None))
#     windows[refresh].show()
#     sys.exit(app.exec_())