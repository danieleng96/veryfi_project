import pyodbc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import config
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import seaborn as sns

high_y = 1.8e-7
low_y = 5e-8
colors = sns.color_palette("bright", 8)


new = [3,2,4,1]
#shane layout
layout = {'b1':['UV40_p','UV40_f','9-20557_f','9-20557_p'],
          'b3':['9008_p','9008_f','OB6235_p','OB6235_f'],
          'b7':['9008_p','9008_f','OB6235_p','empty'],
          'b8':['KE-109-E_p','KE-109-E_f','KE-109-E_f','empty']
          }
class py_sql:
    def __init__(self):
        self.FBN = {'user': 'VL_Fabrinet', 'pwd': r'iku7kRD#234', 'server': 'vl-mes.database.windows.net', 'db':'labview','trusted': 'no'}

        self.STARS = {'user': 'VL_STARS', 'pwd': r'irtfs5#935', 'server': 'vl-mes.database.windows.net', 'db':'labview2','trusted': 'no'}
        self.SJ = {'user': r'VELODYNE\deng', 'pwd': '', 'server': 'vl-mes-db01.velodyne.com', 'db':'labview','trusted': 'yes'}

        self.location = self.SJ
        #sql direct no windows auth
        # self.db = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};'
        #                             'Server=vl-mes-db01.velodyne.com;'
        #                          'Database=labview;'
        #                          'UID=Dazzle;'
        #                          'PWD=DAZpassword321;'
        #                          'Trusted_Connection=no;'
        #                          'Encrypt=no')
        self.db = pyodbc.connect('Driver={SQL Server};'
                          'Server=%s;'
                          'Database=%s;'
                          'UID=%s;'
                          'PWD=%s;'
                          'Trusted_Connection=%s;' % (self.location['server'], self.location['db'],self.location['user'], self.location['pwd'], self.location['trusted']))
        self.cursor = self.db.cursor()

    def analyze_rampup(self, df):
        pass
    def alphas_by_averages(self, column, n):
        #dataframe column, take each group of n to get std_dev
        d = n//2
        alphas = []
        max = 0.0
        for n in range(len(column)):
            #n = 5, d = 50
            #if n > d, n-d:n+d
            #if n <= d, 0:2d
            if n > d and len(column)-n > d:
                n_slice = column[n-d:n+d]
            elif n <= d and len(column) >= 2*d:
                n_slice = column[0:2*d]
            elif len(column)-n < n + d:
                n_slice = column[len(column)-2*d:len(column)]
            # avg = n_slice.mean()
            stdev = n_slice.std()
            # print(stdev)
            if stdev > 1:
                stdev = 1
            if stdev > max:
                max = stdev
            alphas.append(stdev)

        return [x/max for x in alphas]
    def glob_top_data_analysis(self, board, rampup = False):
        import seaborn as sns
        import datetime
        # colors2 = sns.color_palette("dark",16)
        # colors = sns.blend_palette(colors=('#ad0000','#faeb1b','#b305e3','#59c2ff'),n_colors=32)
        # colors = sns.blend_palette(colors=('red','green','purple','orange','blue'),n_colors=32)

        com = f"SELECT * from labview.dbo.Glob_Top_Live_Current where Board_Name = \'{board}\'"
        df = pd.read_sql(com, self.db)
        # print(df['TStamp_start_scan'])
        chs = [f'Ch{n+1}_current' for n in range(32)]
        fig,ax1 = plt.subplots(2,2, sharex = True, sharey = True)
        # print(df['TStamp_start_scan'].iloc[-1])
        # ax1.set_facecolor('lightblue')
        label_cols = []
        for ch in chs:
            mean = abs(df[ch]).mean()
            if mean > low_y:
                if mean < high_y:
                    label_cols.append('green')
                else:
                    #bright red
                    label_cols.append('#ff2e3f')
            else:
                #dark red
                label_cols.append('#990003')
        legend = [[],[],[],[]]
        # df['Elapsed_Time'] = df['Elapsed_Time']/3600
        df = df[df['Temp_Thermocouple'] < 80]
        df['Elapsed_Time'] = df['Elapsed_Time']/60

        if rampup == True:
            df = df[df['Temp_Thermocouple'] < 80]
        else:
            df = df[df['Elapsed_Time'] > 5]
        # print(df.keys())
        ax1[0][0].set_title(f'Dark Current vs Time\nRun 2, KE-109-E 2023-16-01\nRampup starting at grey boundary')

        for n,ch in enumerate(chs):
            g = n//8
            df[ch] = abs(df[ch])

            epoxy = layout['b8'][new[g]-1]
            if g == 0:
                ax = ax1[0][0]
            if g == 1:
                ax = ax1[0][1]
            if g == 2:
                ax = ax1[1][0]
            if g == 3:
                ax = ax1[1][1]

            alphas = self.alphas_by_averages(df[ch], n = 50)

        # group = (n//8)-2

            # df.plot(ax=ax1[group], x="Elapsed_Time", y=ch, kind="scatter", logy=True, figsize=(9, 8),alpha = 0.5, color = colors[n%8])
            # legend[group].append(f'C{n+1}')
            # ax1[group].set_xlabel('Time (hours)', fontweight='bold')
            # ax1[group].set_ylabel('Current (A)', fontweight = 'bold')
            # ax1[group].legend(legend[group],ncol = 2)
            df.plot(ax=ax, x="Elapsed_Time", y=ch, kind="scatter", marker = '.', logy=True, s=200, figsize=(9, 8),alpha = alphas, color = colors[n%8])
            # df.plot(ax=ax, x="Elapsed_Time", y=ch, kind="scatter", marker = '.', logy=True, s=2, figsize=(9, 8),alpha = alphas, color = colors[n%8])

            legend[g].append(f'C{8*(g+1)-n%8}')
            ax.set_xlabel('Time (minutes)', fontweight='bold')
            ax.set_ylabel('Current (A)', fontweight = 'bold')
            # ax.legend(legend[g],ncol = 2, title = f'Group {g+1}\nEpoxy: {epoxy}', loc = 'lower left', labelcolor = label_col)

            leg = ax.legend(legend[g],ncol = 2, title = f'Group {g+1}\nEpoxy: {epoxy}', loc = 'upper left', labelcolor = label_cols[g*8:(g+1)*8])
            if (n+1)%8 == 0:
                for lh in leg.legendHandles:
                    lh._sizes = [30]
                    lh.set_alpha(1)
                # lh.set_sizes(3)/
                # ax.legend(legend[g],ncol = 2, title = f'Group {g+1}\nEpoxy: {epoxy}',title_fontproperties = 'bold')



        for axg in ax1:
            for ax in axg:
                ax.set_facecolor('#fffad1')
                if ax == ax1[0][1]:
                    ax.annotate(text = '⚠Potential Connector issue⚠\nConnector displayed 100x lower current\non initial test', xy = (0.4,0.2), xycoords = 'axes fraction',
                                bbox=dict(boxstyle="square,pad=0.3", fc="yellow",alpha=0.5, ec="k", lw=1))
                ax.fill_between(x = df["Elapsed_Time"], y1 = low_y, y2 = high_y, color = 'lightgreen', alpha = 0.3)
                ax.fill_between(x = df["Elapsed_Time"], y1 = 1, y2 = high_y, color = 'pink', alpha = 0.2)
                ax.fill_between(x = df[df['Temp_Thermocouple'] < 25]["Elapsed_Time"], y1 = 0, y2 = 1, color = 'grey', alpha = 0.2)


                # ax.annotate(text = f'Expected Current Range\n{round(low_y*1e9)}nA-{round(high_y*1e9)}nA', xy= (df["Elapsed_Time"].iloc[-1]-df["Elapsed_Time"].mean()*0.6,low_y),
                #             bbox=dict(boxstyle="square,pad=0.3", fc="lightgreen",alpha=0.5, ec="k", lw=1))
                # ax.set_xlim(0,df["Elapsed_Time"].iloc[-1])
                ax.set_xlim(df["Elapsed_Time"].iloc[0],df["Elapsed_Time"].iloc[-1])

                # ax.set_ylim(5e-10,1e-5)
                ax.set_ylim(1e-12,1e-6)
                ax.set_xlim(df[df['Temp_Thermocouple'] > 22]["Elapsed_Time"].iloc[0]-5,6400/60)




        plt.show()

        return(df)

    #
    def glob_top_enter_line(self, dict):
        question_marks = ''
        keys = ''
        key_list = dict.keys()
        values = []
        for i, key in enumerate(key_list):
            keys += key+','
            question_marks += '?,'
            values.append(dict[key])
        question_marks = question_marks[0:-1]
        keys = keys[0:-1]
        self.cursor = self.db.cursor()

        [num, hour] = self.glob_top_count(dict['Board_Name'])
        values.append(num)
        values.append(hour)
        print(values)
        com = f"INSERT INTO labview.dbo.Glob_Top_Live_Current ({keys},Scan_Number, Elapsed_Time) values({question_marks},?,?)"
        print(com, values)
        try:
            self.cursor.execute(com, values)
            self.db.commit()
        except:
            self.cursor.close()

    def glob_top_count(self, board):
        command = f'Select COUNT(ID)+1 from Glob_Top_Live_Current where Board_Name = \'{board}\' '
        raw = self.cursor.execute(command)

        if raw:
            for num in raw:
                pass
        else:
            num = '1'
        elapsed = f'Select DATEDIFF(second, Min(TStamp_start_scan), GETDATE()) from Glob_Top_Live_Current where Board_Name = \'{board}\''
        hours = self.cursor.execute(elapsed)
        if hours:
            for hour in hours:
                pass
        else:
            hour = '0'
        return [num[0], hour[0]]

    def enter_data(self, df):
        for index, row in df.iterrows():
            self.cursor.execute("INSERT INTO labview.dbo.ApdBreakdown_CH (SerialNumber,Channel,ProductName,APD_breakdown_V,Ch_Duration,Failed,Bin_Voltage,Avg_Leak_Current,STD_Leak_Current,Temp,Temp_Compensated_V, FailureReason) values(?,?,?,?,?,?,?,?,?,?,?,?)", row.SerialNumber, row.Channel, row.ProductName, row.APD_breakdown_V, row.Ch_Duration, row.Failed, row.Bin_Voltage, row.Avg_Leak_Current, row.STD_Leak_Current, row.Temp, row.Temp_Compensated_V, row.FailureReason)
        self.db.commit()
        self.cursor.close()

    def get_platform_commands(self, command_title):
        command = f"Select top 1 velarray_platform + \' \' + full_command from labview.dbo.Platform_Commands where basic_description = \'{command_title}\'"
        raw = self.cursor.execute(command)
        for row in raw:
            pass
        return row

    def enter_ASIC_LP_test(self, df):
        for index, row in df.iterrows():
            cols = 'TestIndex,Channel,SerialNumber,UserNumber,StationNumber,TStamp,Duration,Iteration,Rework,Failed,FailureReason,LP0_high,LP0_Output,LP12_Output,LP14_Output,PRF,REV'
            self.cursor.execute("Insert INTO labview.dbo.")

    def pull_bins(self, sn):
        raw = self.cursor.execute(f"Select BinValue from labview.dbo.SnStatus where SerialNumber = /'{sn}/'")
        for row in raw:
            bin = row
        return bin

    def pull_total_data(self):
        #only passing data
        command = "SELECT SerialNumber, COUNT(APD_breakdown_V) Channel_Count, AVG(cast(APD_breakdown_V as float)) AVG_TROSA, STDEV(cast(APD_breakdown_V as float)) STDEV_TROSA, (AVG(cast(APD_breakdown_V as float)-cast(Bin_Voltage as float))+0.5) AVG_bin_difference, (AVG(cast(APD_breakdown_V as float)-cast(Bin_Voltage as float))+0.5)/AVG(cast(APD_breakdown_V as float))*100 bin_difference_percent from labview.dbo.ApdBreakdown_CH where ABS(cast(bin_voltage as float)) > 5 and failed = 0 and ProductName = 'APA' group by SerialNumber"
        data = pd.read_sql(command, self.db)
        command_ch = "SELECT Channel, COUNT(APD_breakdown_V) Channel_Count, AVG(cast(APD_breakdown_V as float)) AVG_TROSA, STDEV(cast(APD_breakdown_V as float)) STDEV_TROSA, (AVG(cast(APD_breakdown_V as float)-cast(Bin_Voltage as float))+0.5) AVG_bin_difference, (AVG(cast(APD_breakdown_V as float)-cast(Bin_Voltage as float))+0.5)/AVG(cast(APD_breakdown_V as float))*100 bin_difference_percent from labview.dbo.ApdBreakdown_CH where failed = 0 and ProductName = 'APA' group by Channel"
        data_ch = pd.read_sql(command_ch, self.db)
        all_time = "Select SerialNumber, Channel, TStamp, Day(TStamp) Day, DATEPART(hour,TStamp) Hour,cast(APD_Breakdown_V as float)-cast(Bin_Voltage as float) VDiff, cast(APD_Breakdown_V as float) APD_Breakdown from labview.dbo.ApdBreakdown_CH where ABS(cast(bin_voltage as int)) > 5 and Failed = 0 and Channel = 2 and SerialNumber = 'Serial' and ProductName = 'APA' order by TStamp desc"
        time_based = pd.read_sql(all_time, self.db)
        leak_command = "SELECT [SerialNumber],[Channel],[ProductName],[TStamp],[APD_breakdown_V],[Ch_Duration],[Failed],[Bin_Voltage],[Avg_Leak_Current],[STD_Leak_Current],[Temp] FROM [labview].[dbo].[ApdBreakdown_CH] where Avg_Leak_Current is not NULL"
        trosas_with_bins = data[(data["bin_difference_percent"] < 80)]
        # print(data)
        leak_data = pd.read_sql(leak_command, self.db)
        def leak_current_std(df):
            averages = []
            stds = []
            channels = []
            #put in form of averages, std_devs
            for ch in range(config.prod_ch['APA']):
                avg = df[(df['Channel'] == ch)]['Avg_Leak_Current']
                std = df[(df['Channel'] == ch)]['STD_Leak_Current']
                n = len(avg.index)
                print(n)
                x = float(avg.iloc[0])
                x_s = float(std.iloc[0])
                channels.append(ch)
                # print(avg, std)
                for i in range(n-1):
                    print(i)
                    # float(std.iloc[i+1])
                    # float(avg.iloc[i+1])
                    # print(x_s * x)
                    print(str(x) + '+/-'+str(x_s))
                    # x_s =  np.sqrt((((n-1)*x_s**2 + (n-1)*float(std.iloc[i+1]))**2 + 2*n / (n**2) * (x**2 + float(avg.iloc[i+1])**2 - 2 * x * float(avg.iloc[i+1]))) / (2*n -1))
                    x_s = np.sqrt(((n-1)*(x_s**2 + (float(std.iloc[i+1]))**2)+n/2*(x**2 + float(avg.iloc[i+1])**2 - 2*x*float(avg.iloc[i+1])))/(2*n-1))
                    x = (x + avg.iloc[i + 1]) / 2
                averages.append(x)
                stds.append(x_s)
            return averages, stds, channels
        leak_curr, leak_curr_s, chans = leak_current_std(leak_data)
        # fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1,5)
        fig, (ax1, ax2, ax3) = plt.subplots(1,3)
        fig.suptitle('APD Breakdown test data')
        # axs[0].plot(data['AVG_TROSA'], data['bin_difference_percent'], marker = 'o')
        ax1.errorbar(trosas_with_bins['bin_difference_percent'], trosas_with_bins['AVG_TROSA'], yerr = trosas_with_bins['STDEV_TROSA'], marker= 'X', color = '#2F5BFA', linestyle = 'None')
        ax1.set_xlabel('% difference from bin')
        ax1.set_ylabel('Avg APD breakdown across TROSAs (V)')
        ax1.set_title('% off from Bin Value')
        # ax1.set_xscale('log')
        ax1.set_facecolor("#FFA763")

        ax2.errorbar(data['Channel_Count'],data['AVG_TROSA'], yerr = data['STDEV_TROSA'], marker = '*', color = 'purple', linestyle = 'None')
        ax2.set_xlabel('Number of Channels Tested')
        ax2.set_title('# of Channels Tested')
        ax2.set_facecolor("#F7E497")
        ax2.set_xscale('log')

        ax3.errorbar(data_ch['Channel'], data_ch['AVG_TROSA'], yerr=data_ch['STDEV_TROSA'], marker='o', color = 'red', linestyle='None')
        ax3.set_xlabel('Channel')
        ax3.set_title('across all Channels')
        ax3.set_facecolor("#BBB0FF")
        #

        import matplotlib.dates as mdates
        plt.show()

        # df.index[df.curr < -2.00 * 10 ** (-6)][0]
        # day_changes = (time_based['Day'].diff())
        # hour_changes = (time_based['Hour'].diff())
        # # print(day_changes)
        # odd = 0
        # d0 = 0
        # h0 = 0
        # for day_index in day_changes.index[abs(day_changes) > 0]:
        #     # print(day_index)
        #     day_color = ['#34b7eb', "grey"]
        #     d1 = day_index-1
        #     # print(d0,d1)
        #     ax4.axvspan(mdates.date2num(time_based['TStamp'].iloc[d0]), mdates.date2num(time_based['TStamp'].iloc[d1]), color = day_color[odd % 2], alpha = 0.5)
        #     d0 = day_index-1
        #     odd += 1
        # odd = 0
        # for hour_index in hour_changes.index[abs(hour_changes) > 0]:
        #     # print(day_index)
        #     hour_color =['#EED4FF', 'None']
        #
        #     h1 = hour_index-1
        #     # print(d0,d1)
        #     ax4.axvspan(mdates.date2num(time_based['TStamp'].iloc[h0]), mdates.date2num(time_based['TStamp'].iloc[h1]), color = hour_color[odd % 2], alpha = 0.4)
        #     h0 = hour_index-1
        #     odd += 1
        #
        # ax4.plot_date(mdates.date2num(time_based['TStamp']), time_based['VDiff'], marker = '.', color = 'k', linestyle = 'None')
        # ax4.set_xlabel('Time')
        # ax4.set_title('Change from bin value')
        # # mdates.DateLocatortime_based['TStamp'])
        # for tick in ax4.get_xticklabels():
        #     tick.set_rotation(45)
        # ax4.set_ylabel('V Diff (bin vs tested)')
        # leak_curr = [i *1e9 for i in leak_curr]
        # leak_curr_s = [i * 1e9 for i in leak_curr_s]
        # # leak_data = data.dropna(threshold = '2')
        # ax5.errorbar(chans,leak_curr, yerr = leak_curr_s, marker = '*', color = 'purple', linestyle = 'None')
        # ax5.set_xlabel('Channel')
        # ax5.set_ylabel('Avg Leak Current nA')
        # ax5.set_title('Leak Current vs Channel')
        # ax5.set_facecolor('yellow')
    # def analysis(self):

        # print(data)

    def meeting_data(self):
        #only passing data
        command_pie = "WITH most_recent AS (\
          SELECT m.*, ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TStamp DESC) AS rn\
          FROM labview.dbo.ApdBreakdown_CH AS m\
        ),\
        c as (SELECT TStamp, FailureReason, rn, Temp_Compensated_V, Failed, SerialNumber, Channel, (Max(cast(Temp_Compensated_V as float)) OVER (Partition BY SerialNumber order by TStamp desc) - MIN(cast(Temp_Compensated_V as float)) OVER (Partition BY SerialNumber order by TStamp desc)) Ch_dif\
          FROM most_recent AS b where rn <= 4), g_5 as (Select FailureReason, rn, Temp_compensated_V, Failed, SerialNumber, TStamp, Ch_dif from c) Select Temp_Compensated_V, Failed, FailureReason, g_5.SerialNumber,g_5.TStamp ,Ch_dif from g_5 join SnStatus on SnStatus.SerialNumber = g_5.SerialNumber where cast(Temp_Compensated_V as float) is not NULL and SnStatus.ProductName = \'APA\' and rn = 4 order by g_5.TStamp desc"\
        # print(command_pie)
        command_pie_ch = 'WITH most_recent AS (\
  SELECT m.*, ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TStamp DESC) AS rn\
  FROM labview.dbo.ApdBreakdown_CH AS m\
),\
c as (SELECT FailureReason, rn, Temp_Compensated_V, Failed, SerialNumber, Channel, (Max(cast(Temp_Compensated_V as float)) OVER (Partition BY SerialNumber order by TStamp desc) - MIN(cast(Temp_Compensated_V as float)) OVER (Partition BY SerialNumber order by TStamp desc)) Ch_dif\
  FROM most_recent AS b where rn <= 4),\
g_5 as (Select FailureReason, rn, Temp_compensated_V, Failed, SerialNumber, Channel, Ch_dif from c)\
  Select SnStatus.ProductName, Temp_Compensated_V, Failed, FailureReason, g_5.SerialNumber, Channel, Ch_dif from g_5 \
  join SnStatus on SnStatus.SerialNumber = g_5.SerialNumber\
  where cast(Temp_Compensated_V as float) is not NULL and SnStatus.ProductName = \'APA\'\
  order by Ch_dif desc'
        pie_data_ch = pd.read_sql(command_pie_ch, self.db)
        pie_data = pd.read_sql(command_pie, self.db)
        command = "SELECT SerialNumber, COUNT(Temp_Compensated_V) Channel_Count, AVG(cast(Temp_Compensated_V as float)) AVG_TROSA, AVG(cast(Bin_Voltage as float)) BV, STDEV(cast(Temp_Compensated_V as float)) STDEV_TROSA, (AVG(cast(Temp_Compensated_V as float)-cast(Bin_Voltage as float))+0.5) AVG_bin_difference, (AVG(cast(Temp_Compensated_V as float)-cast(Bin_Voltage as float))+0.5)/AVG(cast(Temp_Compensated_V as float))*100 bin_difference_percent from labview.dbo.ApdBreakdown_CH where ABS(cast(bin_voltage as float)) > 5 and (ABS(cast(APD_Breakdown_V as float)) > 120 and ABS(cast(APD_Breakdown_V as float)) < 215) and Temp_Compensated_V is not Null and ProductName = 'APA' group by SerialNumber"
        data = pd.read_sql(command, self.db)
        command_ch = "SELECT Channel, COUNT(APD_breakdown_V) Channel_Count, AVG(cast(APD_breakdown_V as float)) AVG_TROSA, STDEV(cast(APD_breakdown_V as float)) STDEV_TROSA, (AVG(cast(APD_breakdown_V as float)-cast(Bin_Voltage as float))+0.5) AVG_bin_difference, (AVG(cast(APD_breakdown_V as float)-cast(Bin_Voltage as float))+0.5)/AVG(cast(APD_breakdown_V as float))*100 bin_difference_percent from labview.dbo.ApdBreakdown_CH where failed = 0 and ProductName = 'APA' group by Channel"
        data_ch = pd.read_sql(command_ch, self.db)
        all_time = "Select SerialNumber, Channel, TStamp, Day(TStamp) Day, DATEPART(hour,TStamp) Hour,cast(APD_Breakdown_V as float)-cast(Bin_Voltage as float) VDiff, cast(APD_Breakdown_V as float) APD_Breakdown, cast(Temp_Compensated_V as float) V_t,ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TStamp DESC) AS rn from labview.dbo.ApdBreakdown_CH where (ABS(cast(APD_Breakdown_V as float)) > 120 and ABS(cast(APD_Breakdown_V as float)) < 215) and Temp_Compensated_V is not Null and ProductName = 'APA' order by TStamp desc"
        time_df = pd.read_sql(all_time, self.db)
        reliability = 'select Channel, APD_Breakdown_V BD from ApdBreakdown_CH where SerialNumber = \'L260-0316\' and Channel !=7 and cast(APD_breakdown_V as float) < -100 '
        reliability = pd.read_sql(reliability, self.db)
        trosa_spread = "with a as (Select SerialNumber, Channel, TStamp, cast(APD_Breakdown_V as float)-cast(Bin_Voltage as float) VDiff, ROW_NUMBER() OVER (PARTITION BY SerialNumber ORDER BY TStamp DESC) rn, cast(APD_Breakdown_V as float) APD_Breakdown, cast(Bin_Voltage as float) Bin, cast(Temp_Compensated_V as float) V_t from labview.dbo.ApdBreakdown_CH where Temp_Compensated_V is not Null and ProductName = 'APA' and (ABS(cast(bin_voltage as float)) > 120 or abs(cast(Temp_Compensated_V as float)) < 215))"\
        "Select a.SerialNumber, MAX(a.V_t)-MIN(a.V_t) spread from a where rn <= 4 group by a.SerialNumber order by spread"
        trosa_spread_df = pd.read_sql(trosa_spread, self.db)
        trosas_with_bins = data[(data["bin_difference_percent"] < 80)]
        fig, (ax1, ax2) = plt.subplots(1,2)
        fig, (ax3, ax4) = plt.subplots(1,2)
        fig.suptitle('APD Breakdown test data')
        # axs[0].plot(data['AVG_TROSA'], data['bin_difference_percent'], marker = 'o')
        ax1.plot([-205, -170], [-205, -170], alpha = 0.5)
        ax1.errorbar(trosas_with_bins['BV'], trosas_with_bins['AVG_TROSA'], yerr = trosas_with_bins['STDEV_TROSA'], marker= 'X', color = '#2F5BFA', linestyle = 'None')
        ax1.set_xlabel('Bin Breakdown (V')
        ax1.set_xlim([-205, -170])
        ax1.set_ylim([-205, -170])
        ax1.grid(color='blue', linestyle='-', linewidth=1, alpha=0.1, which ='both')
        ax1.yaxis.set_minor_locator(MultipleLocator(1))
        ax1.xaxis.set_minor_locator(MultipleLocator(1))
        ax1.set_ylabel('Measured APD Breakdown (V)')
        ax1.set_title('Bin Voltage vs Measured Breakdown')
        # ax1.set_xscale('log')
        ax1.set_facecolor("#FFA763")
        rel_boxes = []
        avgs = []
        r = []
        diffs = []
        for x in range(7):
            rel = reliability[(reliability['Channel'] == x)]['BD'].astype(float)
            rel_boxes.append(rel)
            avgs.append(rel.mean())
            diffs.append(round(rel.max() - rel.min(),ndigits =2))
            r.append(float(x))
        # m, b = np.polyfit(r,avgs,1)
        # print(rel_boxes)
        print(diffs)
        # ax2.boxplot([reliability[(reliability['Channel']== 0)]['BD'],reliability[(reliability['Channel']== 1)]['BD'],reliability[(reliability['Channel']== 2)]['BD'],reliability[(reliability['Channel']== 3)]['BD'],reliability[(reliability['Channel']== 4)]['BD'],reliability[(reliability['Channel']== 5)]['BD'],reliability[(reliability['Channel']== 6)]['BD']], showfliers = True)
        ax2.boxplot(rel_boxes, showfliers = True)
        # ax2.plot(r,float(m)*r+b,alpha = 0.5)
        ax2.set_xlabel('Channels')
        ax2.set_title('Breakdown Voltages Reliability (n=70)\nBefore Temperature Compensation')
        ax2.set_ylim([-190, -180])
        ax2.set_facecolor("#F7E497")
        ax2.grid(color='k', linestyle='-', linewidth=1, alpha=0.1, axis = 'y', which = 'both')
        ax2.yaxis.set_major_locator(MultipleLocator(5))
        ax2.yaxis.set_minor_locator(MultipleLocator(1))
        # ax2.set_xscale('log')
        # plt.show()
        # print(time_df)
        ax3.boxplot([time_df[(time_df['Channel']  == 0)]['V_t'], time_df[(time_df['Channel']  == 1)]['V_t'], time_df[(time_df['Channel']  == 2)]['V_t'], time_df[(time_df['Channel']  == 3)]['V_t']],  showfliers = True)

        # ax3.boxplot([data_ch[(data_ch['Channel']  == 0)]['AVG_TROSA'], data_ch[(data_ch['Channel'] == 1)]['AVG_TROSA'], data_ch[(data_ch['Channel'] == 2)]['AVG_TROSA'], data_ch[(data_ch['Channel'] == 3)]['AVG_TROSA']])
        ax3.set_xlabel('Channel')
        ax3.set_title('Breakdown Voltage across all Channels')
        ax3.set_ylabel('Breakdown Voltage (V)')
        ax3.set_facecolor("#BBB0FF")
        ax3.grid(color='k', linestyle='-', linewidth=1, alpha = 0.1, axis = 'y')

        spread = trosa_spread_df[(trosa_spread_df['spread'] < 20)]
        # ran = round(spread.max()-spread.min())
        bins_list = [0,1,2,3,4,5,6,7,8,9,10]
        ax4.hist(spread['spread'], bins = bins_list)
        # ax4.boxplot(spread[(spread['spread']%1 == 0)]['spread'], spread[(spread['spread']%1 != 0)]['spread'], showfliers = True)
        ax4.set_xlabel('Voltage Spread Between Channels (V)')
        ax4.set_title('Voltage Spread Between Channels\nMax - Min (V)')
        ax4.grid(color='k', linestyle='-', linewidth=1, alpha=0.1)
        ax4.set_xlim([0,10])
        ax4.xaxis.set_major_locator(MultipleLocator(1))
        ax4.yaxis.set_minor_locator(MultipleLocator(1))
#channel
        ch_total = len(pie_data_ch.index)
        # ch_non_con_fail = pie_data_ch['Failed'].sum()
        # print(pie_data['Temp_Compensated_V'].sort_values())
        ch_zeroes = len(pie_data_ch[(abs(pie_data_ch['Temp_Compensated_V'].astype(float)) < 100)])
        ch_nonzeroes = len(pie_data_ch[(abs(pie_data_ch['Temp_Compensated_V'].astype(float)) > 210)])
        print("CHS: ", ch_total, ch_zeroes, ch_nonzeroes)
        # ch_total = 356
        pie_ch_totals = [ch_total-ch_zeroes - ch_nonzeroes,ch_zeroes,ch_nonzeroes]
#TROSA

        total = len(pie_data.index)
        non_con_fail = pie_data['Failed'].sum()
        gt_5_spread = len(pie_data[(pie_data['Ch_dif'] > 5) & (abs(pie_data['Temp_Compensated_V'].astype(float)) < 210) & (abs(pie_data['Temp_Compensated_V'].astype(float)) > 100)])
        gt_3_spread = len(pie_data[(pie_data['Ch_dif'] > 3) & (abs(pie_data['Temp_Compensated_V'].astype(float)) < 210) & (abs(pie_data['Temp_Compensated_V'].astype(float)) > 100)])
        lt_5_spread = len(pie_data[(pie_data['Ch_dif'] < 5) & (abs(pie_data['Temp_Compensated_V'].astype(float)) < 210) & (abs(pie_data['Temp_Compensated_V'].astype(float)) > 100)])
        lt_3_spread = len(pie_data[(pie_data['Ch_dif'] < 3) & (abs(pie_data['Temp_Compensated_V'].astype(float)) < 210) & (abs(pie_data['Temp_Compensated_V'].astype(float)) > 100)])
        # print(pie_data['Temp_Compensated_V'].sort_values())
        zeroes = len(pie_data[(abs(pie_data['Temp_Compensated_V'].astype(float)) < 100) & (pie_data['Temp_Compensated_V'].isnull() == False)])
        nonzeroes = len(pie_data[(abs(pie_data['Temp_Compensated_V'].astype(float)) > 210)])
        print("Numbers: ", total, non_con_fail, gt_5_spread, gt_3_spread, lt_5_spread, lt_3_spread,zeroes, nonzeroes)
        out_of_spec = len(pie_data[(pie_data['FailureReason'] == '>10V_out_of_Bin')])

        # gt_3_spread = 11
        # gt_5_spread = 1
        # lt_5_spread = 79
        # lt_3_spread = 69
        pie_TROSA_pass = [lt_3_spread,gt_3_spread]
        pie_TROSA_spread = [total-out_of_spec, out_of_spec]
        pie_TROSA_totals = [lt_3_spread,gt_3_spread,zeroes,nonzeroes]
        pie_TROSA_totals_5 = [lt_5_spread,gt_5_spread,zeroes,nonzeroes]

        fig, (ax5, ax6) = plt.subplots(1, 2)
        explode_ch = (0, 0.4, 0.2)
        explode_trosa = (0, 0.3, 0.4, .1)
        color_out_spec = ['#67c6e6','#ed6d94']
        color_ch = ['#92de6d', '#ff7105', '#ff5252']
        color_trosa = ['#92de6d','#ffd152','#ff7105','#ff5252']
        ax5.pie(pie_TROSA_totals_5, explode=explode_trosa, autopct='%1.1f%%',
                labels=['Spread < 5V', 'Spread > 5V', 'Zero V Fail', 'Non-Zero Fails'],
                colors=color_trosa)
        ax5.set_title(f'TROSA specific APA Failure breakdown (5V spread) n = {total} TROSAs')
        ax6.pie(pie_TROSA_totals, explode=explode_trosa, autopct='%1.1f%%',
                labels=['Spread < 3V', 'Spread > 3V', 'Zero V Fail', 'Non-Zero Fails'],
                colors=color_trosa)
        ax6.set_title(f'TROSA specific APA Failure breakdown (3V spread) n = {total} TROSAs')
        fig, (ax7, ax8) = plt.subplots(1, 2)
        ax7.pie(pie_ch_totals, explode=explode_ch, autopct='%1.1f%%',
                labels=['Converging channels', 'Zero V Fail', 'Non-Zero Fails'], colors=color_ch)
        ax7.set_title(f'Channel specific APA Failure breakdown, n = {ch_total} channels')
        ax8.pie(pie_TROSA_spread, autopct='%1.1f%%',
                labels=['within 10V of bin', '>10V out of bin'], colors=color_out_spec)
        ax8.set_title(f'Out of bin by 10V, n = {total}')
        plt.show()
        # ax3.errorbar(data_ch['Channel'], data_ch['AVG_TROSA'], yerr=data_ch['STDEV_TROSA'], marker='o', color = 'red', linestyle='None')
        # ax3.set_xlabel('Channel')
        # ax3.set_title('across all Channels')
        # ax3.set_facecolor("#BBB0FF")
        # plt.show()
if __name__ == '__main__':
    # print(py_sql().meeting_data())
    print(py_sql().glob_top_data_analysis('b8g1,b8g2,b8g3,b8g4'))
    # py_sql().analysis()

    # py_sql().pull_total_data() 