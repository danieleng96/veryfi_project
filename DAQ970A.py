#!/usr/bin/python
# import visa
import pyvisa
import pandas as pd
import SourceMeter as SourceMeter
import SQL_server as sql
# import MySQLdb
import time
import numpy as np
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import TC_720 as temp
import SQL_server as sql




# import schedule # To schedule time for the program to execute


class DAQ970A:
    # def __init__(self, serial='USB0::0x2A8D::0x5101::MY58006426::INSTR'):

    def __init__(self, serial='USB0::10893::20737::MY58006426::INSTR'):
    # def __init__(self, serial='ASRL5::INSTR'):

        self.rm = pyvisa.ResourceManager()
        print(self.rm.list_resources())
        self.dev = self.rm.open_resource(serial, open_timeout=1500)
        dev_info = self.dev.query('*IDN?')
        print(dev_info)
        self.channels= ['@311','@312','@313','@314','@315','@316','@317','@318']
        self.channel_str = '@311,312,313,314,315,316,317,318'
        self.sql = sql.py_sql()
        self.temp = temp.TC720()
        self.mux_channels= ['@201','@202','@203','@204','@205','@206','@207','@208', '@209', '@210', '@211', '@212', '@213', '@214', '@215', '@216', '@217', '@218', '@219', '@220', '@221', '@222', '@223', '@224', '@225', '@226', '@227', '@228', '@229', '@230', '@231', '@232']
        self.mux_channel_str = '@201:232'
        # self.SLEEP_TIME = 1800
        self.SLEEP_TIME = 30

    # print(dev.query(self.open))
    # time.sleep(0.5)
    # er.write("*CLS")
    # time.sleep(0.5)
    # er.write("ROUT:SCAN (@303)")
    # time.sleep(0.5)
    # er.write("CONF:TEMP (@203)")
    # fig = plt.figure()
    # ax1 = fig.add_subplot(1, 1, 1)
    #
    # def animate(self,data_dic):
    #     pullData = open("sampleText.txt", "r").read()
    #     dataArray = pullData.split('\n')
    #     xar = []
    #     yar = []
    #     for eachLine in dataArray:
    #         if len(eachLine) > 1:
    #             x, y = eachLine.split(',')
    #             xar.append(int(x))
    #             yar.append(int(y))
    #     ax1.clear()
    #     ax1.plot(xar, yar)
    #
    # ani = animation.FuncAnimation(fig, animate, interval=1000)
    # plt.show()
    #channels are a three digit number, (slot,row,column)
    def get_id(self):
        return self.dev.query("*IDN?")

    def get_output(self):
        return self.dev.query("OUTP?")

    def set_samples(self, samples = 100):
        self.dev.write(f"SAMP:COUN {samples}"
                       )

    def set_output(self, state):
        self.dev.write(f"OUTP {state}")



    #
    # def get_source_func(self):
    #     return self.dev.query("SOUR:FUNC?")

    def close_exclusive(self, channels):
        # if type(channels) == 'list':
        #     ch_str = ['@']
        #     for ch in channels:
       self.dev.write(f"ROUT:CLOS:EXCL ({channels})")

    def open_channels(self, channels):
        self.dev.write(f"ROUT:OPEN ({channels})")

    def close_channels(self, channels):
        self.dev.write(f"ROUT:CLOS ({channels})")

    def check_channels(self, channels):
        return self.dev.query(f"ROUT:OPEN? ({channels})")

    # DATABASE, Pandas


    ## using MUX

    def read_single_voltage(self, channels, range = 0.2, res = 0.001, trig_count = 10):
        # self.dev.write(f"MEAS:VOLT:DC ({channels})")

        self.dev.write(f"CONF:VOLT:DC ({channels})")
        # self.dev.write(f"TRIG SOUR EXT")

        return self.dev.query("READ?")

        # f"ACQ:VOLT:DC   1, 100, 0.01, ({channels})"
        # TRIG: SOUR
        # INT
        # TRIG: LEV
        # 0.75
        # TRIG: SLOP
        # POS


        # return self.dev.query(f"MEAS:VOLT:DC? {range},{res} ({channels})")

        # return self.dev.query("MEAS:VOLT:DC? 10,0.001 @201")

    # def read_single_voltage(self, channels, type = 'ALL?'):
    #     return self.dev.query(f"CALC:AVER:{type} ({channels})")

    def clear_multiplexer_voltage(self,channels):
        self.dev.write(f"CALC:AVER:CLE ({channels})")

    def dmm_on(self, on_off = 'ON'):
        # pass
        print(self.dev.query("INST:DMM?"))
        self.dev.write(f"INST:DMM {on_off}")

    def run_each(self):
        # self.dev.write("*RST")
        # print(self.check_channels(self.mux_channel_str))
        # board_name = input('Enter board name or number: ')
        board_name = """b8g1,b8g2,b8g3,b8g4"""
        self.dmm_on()
        self.clear_multiplexer_voltage(self.mux_channel_str)
        total_data = {}

        self.close_channels(self.mux_channel_str)
        time.sleep(1)

        for i in range(9000):
            if i != 0:
                time.sleep(self.SLEEP_TIME)

            channel_all = {'Board_Name': board_name}
            temperature = self.temp.get_temp()
            # temperature = 25
            # temperature = 85
            channel_all['Temp_Thermocouple'] = temperature
            for n, ch in enumerate(self.mux_channels):
                # print(self.check_channels(self.mux_channel_str))
                tag = f'Ch{n+1}_current'
                # self.open_channels(self.mux_channel_str)
                # leak = self.read_single_voltage(ch)
                bias_voltage = 150
                resistance = 20e6

                # self.close_channels(ch)
                # self.set_samples(100)
                t = time.time()
                ch_all_data = self.read_single_voltage(ch)
                # ch_all_data = 5


                print(f"{i}: V_{ch} = {ch_all_data} V")
                # channel_average.append(ch_all_data[2])
                current = float(ch_all_data) / float(resistance)
                total_data.setdefault(tag, []).append(current)
                channel_all[tag]=current

                self.clear_multiplexer_voltage(self.mux_channel_str)

                    # self.open_channels(self.mux_channel_str)
                # x=0
                # while x:
            tries = 30
            for n in range(tries):
                try:
                    #local changes, need to save sql
                    self.sql.glob_top_enter_line(channel_all)
                    print(n)
                except:
                    time.sleep(15)
                    print('Failed: iteration', n)
                    continue
                break


        fig,ax = plt.subplots()
        keys =list(total_data.keys())

        colors = [(0,0,1),(0,1,0),(1,0,0),(1,1,0),(.5,0,1),(0,.5,1),(1,.5,.1),(.5,.75,0)]
        NUM_COLORS = len(keys)
        cm = plt.get_cmap('gist_rainbow')
        # cNorm = colors.Normalize(vmin=0, vmax=NUM_COLORS - 1)
        # scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
        print(keys)
        for n,k in enumerate(keys):
            # set_color(cm(i // 3 * 3.0 / NUM_COLORS))
            x,current = range(len(total_data[k])), total_data[k]
            # ax.scatter(x,current, c =colors[n])
            # ax.scatter(x,current, c =cm(i // 3 * 3.0 / NUM_COLORS))
            ax.scatter(x,current)

            # ax.fill_between(x,current, alpha = 0.1, color = colors[n])
            # ax.fill_between(x, current, alpha=0.1, color= cm(i // 3 * 3.0 / NUM_COLORS))
            # ax.fill_between(x, current, alpha=0.1)
            # ax.set_ylim([-0.5e-9,0])
            ax.set_title('Current vs Time (Bias V=160V, Temp = 26C)')
            ax.set_ylabel('Dark current (I)')
            ax.set_xlabel('samples')
        # patch = patches.Patch(color=colors, label=keys)
        # ax.legend(handles=[patch])
        ax.legend()

        print(total_data)
        plt.show()

def prev_main():
    sm = SourceMeter.Keithley_2400()
    dq = DAQ970A()
    dq.open_channels(dq.channel_str)
    # dq.close_channels('@318')
    # sm.set_IV_curve_sweep()
    # n=1
    # sm.run_IV_curve(f'open_test{n}')
    # dq.open_channels('@318')
    # dq.close_channels('@317')
    # sm.set_IV_curve_sweep()
    # n=2
    # sm.run_IV_curve(f'open_test{n}')
    # dq.open_channels('@317')
    for n, ch in enumerate(dq.channels):
        dq.close_channels(ch)
        time.sleep(1)
        print(f'Channel {n+1}')
        #
        sm.set_IV_curve_sweep()
        sm.run_IV_curve(f'closed_test{n}')
        # time.sleep(1)
        dq.open_channels((ch))
        # sm.set_IV_curve_sweep()
        # sm.run_IV_curve(f'open_test{n}')
        # # print(dq.check_channels(ch))


if __name__ == '__main__':
    dq = DAQ970A()
    dq.run_each()
    # dq = DAQ970A().close_channels('@311,312,313,314,315,316,317,318')


# try:
#     db=MySQLdb.connect("127.0.0.1", "nectec", "1q2w3e4r", "Temperaturedb")
#     curs=db.cursor()
#     print("Successfully connected to Database")
#     update=True
#     while update:
#         def job():
#            from datetime import datetime
#            now=datetime.now()
#            datetime=now.strftime('%Y-%m-%d %H:%M:%S')
#            #time.sleep(0.5)
#            temp = {}
#            er.write("MEAS:TEMP? (@203)")
#            temp['value']=float(er.read())
#            qq=temp['value']
#            print("%.2f" % qq)
#            #time.sleep(0.5)
#            curs.execute("INSERT INTO DAQ970A_DATA VALUES (%s, %s)", (datetime, qq, ))
#            #time.sleep(0.5)
#            print("Data uploaded to Database")
#            db.commit()
#
#            #time.sleep(5)
#         schedule.every(10).minutes.do(job)
#         while True:
#             schedule.run_pending()
#
# except Exception as e:
#       print (e)
#       update=False
#       curs.close
#       db.close
