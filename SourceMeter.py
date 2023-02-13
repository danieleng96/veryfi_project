import pyvisa
from math import ceil
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import config
import DAQ970A as daq
import random
import os

TIMEOUT = 10
MAX_NUM_DATA_POINTS = 2500
MAX_NUM_CUST_DATA_POINTS = 100
# BAUD_RATE = 19200
BAUD_RATE = 57600


class Keithley_2400:
    def __init__(self, serial='ASRL3::INSTR'):
        self.rm = pyvisa.ResourceManager('@py')
        # self.rm = pyvisa.ResourceManager()

        serial = self.rm.list_resources()[0]
        print(serial)
        # with self.rm.open_resource('ASRL3::INSTR') as Power_Analysor:
        #     print(Power_Analysor.query('*IDN?'))
        #     print(Power_Analysor)

        self.dev = self.rm.open_resource(serial, baud_rate=BAUD_RATE, read_termination='\r', timeout=TIMEOUT * 1000)
        dev_info = self.dev.query('*IDN?')
        print(dev_info)

        try:
            self.dq = daq.DAQ970A()
        except:
            self.dq = None

    def get_id(self):
        return self.dev.query("*IDN?")

    def get_output(self):
        return self.dev.query("OUTP?")

    def set_output(self, state):
        self.dev.write(f"OUTP {state}")

    def get_source_func(self):
        return self.dev.query("SOUR:FUNC?")

    def set_source_func(self, func):
        self.dev.write(f"SOUR:FUNC {func}")

    def set_sweep(self, mode, start, stop, step, delay):
        if mode == 'VOLT':
            sense = 'CURR'
        elif mode == 'CURR':
            sense = 'VOLT'
        else:
            raise RuntimeError(f'{mode} is an invalid mode!')
        data_points = abs(ceil((stop - start) / step)) + 1
        if data_points > MAX_NUM_DATA_POINTS:
            raise RuntimeError(f'Sweep has too many points {data_points}, must be {MAX_NUM_DATA_POINTS} or less!')
        print(f'Setting sweep with {data_points} data points...')
        # self.dev.write("*RST")
        self.dev.write("SOUR:FUNC VOLT")
        self.dev.write("SOUR:VOLT:MODE FIXED")
        self.dev.write("SENS:CURR:PROT 3e-6")
        self.dev.write("SENS:FUNC:CONC OFF")
        self.dev.write(f"SOUR:{mode}:MODE SWE")
        self.dev.write(f"SENS:FUNC '{sense}:DC'")
        self.dev.write(f"SOUR:{mode}:START {start}")
        self.dev.write(f"SOUR:{mode}:STOP {stop}")
        self.dev.write(f"SOUR:{mode}:STEP {step}")
        self.dev.write(f"SOUR:SWE:RANG AUTO")
        self.dev.write(f"SOUR:SWE:SPAC LIN")
        self.dev.write(f"TRIG:COUN {data_points}")
        self.dev.write(f"SOUR:SWE:POIN {data_points}")
        self.dev.write(f"SOUR:DEL {delay}")

    def find_leak_current(self, mode, set_point, data_points, delay = .001):
        #find leak current at breakdown - 40V, no ramp
        if mode == 'VOLT':
            sense = 'CURR'
        elif mode == 'CURR':
            sense = 'VOLT'
        else:
            raise RuntimeError(f'{mode} is an invalid mode!')
        self.dev.write("SENS:CURR:PROT 3e-6")
        self.dev.write("SENS:FUNC:CONC OFF")
        self.dev.write(f"SOUR:FUNC {mode}")
        self.dev.write(f"SENS:FUNC '{sense}:DC'")
        self.dev.write(f"TRIG:COUN {data_points}")
        self.dev.write(f"SOUR:DEL {delay}")

        self.run_sweep()

    def set_cust_sweep(self, mode, source_list, delay):
        if mode == 'VOLT':
            sense = 'CURR'
        elif mode == 'CURR':
            sense = 'VOLT'
        else:
            raise RuntimeError(f'{mode} is an invalid mode!')
        data_points = len(source_list)
        if data_points > MAX_NUM_CUST_DATA_POINTS:
            raise RuntimeError(f'Sweep has too many points {data_points}, must be {MAX_NUM_DATA_POINTS} or less!')
        print(f'Setting sweep with {data_points} data points...')
        arr = [str(x) for x in source_list]
        data_list = ",".join(arr)
        # self.dev.write("*RST")
        self.dev.write("SENS:CURR:PROT 3e-6")
        self.dev.write("SENS:FUNC:CONC OFF")
        self.dev.write(f"SOUR:FUNC {mode}")
        self.dev.write(f"SENS:FUNC {sense}:DC")
        self.dev.write(f"SOUR:{mode}:MODE LIST")
        self.dev.write(f"SOUR:SWE:RANG AUTO")
        time.sleep(6)
        self.dev.write(f"SOUR:LIST:{mode} {data_list}")
        self.dev.write(f"TRIG:COUN {data_points}")
        self.dev.write(f"SOUR:DEL {delay}")

    def get_sweep_dir(self):
        return self.dev.query("SOUR:SWE:DIREction?")

    def set_sweep_dir(self, dir):
        self.dev.write(f"SOUR:SWE:DIREction {dir}")

    def run_sweep(self):
        print('Running sweep...')
        self.set_output('ON')
        self.dev.write("INIT")
        self.dev.write("*WAI")
        self.set_output('OFF')
        self.dev.write("*WAI")
        # input("Press 'Enter' when data collection has finished\n")
        time.sleep(3)
        print('Fetching data...')
        return self.dev.query('FETC?')



    # @staticmethod
    # def parse_buffer(buff):
    #     print('Parsing data...')
    #     buff_arr = buff.split(',')
    #     dec_data = {}
    #     fields = ['volt', 'curr', 'res', 'time', 'status']
    #     for i, field in enumerate(fields):
    #         dec_data[field] = []
    #         for j in range(int(len(buff_arr) / len(fields))):
    #             if field == 'status':
    #                 dec_data[field].append(int(float(buff_arr[(j * len(fields)) + i])))
    #             else:
    #                 dec_data[field].append(float(buff_arr[(j * len(fields)) + i]))
    #     df = pd.DataFrame.from_dict(dec_data)
    #     # print(df)
    #     print(df.curr.std())
    #     breakdown = df[df.curr < -2*10**(-6)].iloc[0].volt
    #     print(breakdown)
    #     #return dataframe
    #     return df, breakdown

    @staticmethod
    def parse_buffer(buff):
        #channel specific
        #count_skip

        print('Parsing data...')
        buff_arr = buff.split(',')
        dec_data = {}
        fields = ['volt', 'curr', 'res', 'time', 'status']
        for i, field in enumerate(fields):
            dec_data[field] = []
            for j in range(int(len(buff_arr) / len(fields))):
                if field == 'status':
                    dec_data[field].append(int(float(buff_arr[(j * len(fields)) + i])))
                else:
                    dec_data[field].append(float(buff_arr[(j * len(fields)) + i]))
        return dec_data

    @staticmethod
    def parse_buffer_volt_curr(buff):
        # channel specific
        # count_skip

        print('Parsing data...')
        buff_arr = buff.split(',')
        dec_data = {}
        fields = ['volt', 'curr', 'res', 'time', 'status']
        for i, field in enumerate(fields):
            dec_data[field] = []
            for j in range(int(len(buff_arr) / len(fields))):
                if field == 'status':
                    dec_data[field].append(int(float(buff_arr[(j * len(fields)) + i])))
                else:
                    dec_data[field].append(float(buff_arr[(j * len(fields)) + i]))
        return dec_data['volt','curr']


    def breakdown_processing(self, buff):
        dec_data = self.parse_buffer(buff)
        skip = 22
        frame = pd.DataFrame.from_dict(dec_data)
        leak_curr = frame.curr.iloc[2:18]
        # print("leak curr", leak_curr)
        avg_leak = leak_curr.mean()
        std_leak = leak_curr.std()
        print("leak_curr:",avg_leak)
        df = frame.iloc[skip:]
        delta = df.curr.diff().iloc[1:]
        print("STD: ", df.curr.std())
        biggest_drop = delta.min()
        try:

            bd_index = df.index[df.curr < -2.00 * 10 ** (-6)][0]

            #interpolate to find exactly -2 uA voltage
            x_0 = df.iloc[bd_index-skip-1].volt
            x_1 = df.iloc[bd_index-skip].volt
            y_0 = df.iloc[bd_index-skip-1].curr
            y_1 = df.iloc[bd_index-skip].curr
            # try:
            breakdown = ((-2.00*10**(-6))-y_0)*(x_1-x_0)/(y_1-y_0)+x_0
            # except:
            #     breakdown = 0

            def find_neighbours(value, df, colname):
                exactmatch = df[df[colname] == value]
                if not exactmatch.empty:
                    return exactmatch.index
                else:
                    lowerneighbour_ind = df[df[colname] < value][colname].idxmax()
                    upperneighbour_ind = df[df[colname] > value][colname].idxmin()
                    return [lowerneighbour_ind, upperneighbour_ind]

            fail = 0
        except:
            breakdown = 0
            fail = 1
        print("Breakdown voltage: "+ str(breakdown))
        #return dataframe
        return dec_data, df, breakdown, avg_leak, std_leak

    @staticmethod
    def dump_to_csv(dec_data, file):
        print('Writing data to file...')
        import csv
        results_dict = {}
        with open(file, 'w') as results_file:
            csv_writer = csv.DictWriter(results_file, fieldnames=[key for key in dec_data], lineterminator='\n')
            csv_writer.writeheader()
            for i in range(len(list(dec_data.values())[0])):
                for key in dec_data:
                    results_dict[key] = dec_data[key][i]
                csv_writer.writerow(results_dict)

    # def save_finish(self, sn, product='TROSA_101', plot = False):
    #     labels = ["SerialNumber", "Channel", "APD_breakdown_V", "Failed"]
    #     ch_data = []
    #     colors = ['r','b','g','k','teal','navy','purple','yellow']
    #     for ch in range(config.prod_ch[product]):
    #         plt.plot()
    #         plt.plot(dec_data['volt'], dec_data['curr'])
    #         plt.xlabel('Voltage (V)')
    #         plt.ylabel('Current (A)')
    #         plt.show()

        #channel data, save whole dataframe. Plot all channels and breakdown voltages (full scans?)

        # Need to run each channel:
        # meaning for each channel, set up sweep, run sweep, parse data
        # plot after all channels have finished

        # def full_test(self, product, serial_number):
        #   for each channel:
        #
        #
        #
        #
    def pre_sweep(self):
        arr = np.linspace(-130, -210, 50)
        self.set_cust_sweep('VOLT', arr, 0.001)

    def run_and_dump_data(self, name, plot=False):
        file = 'C:\\Users\\ndondlinger\\Documents\\V8\\HV_failure\\IV_Curves\\' + name + '.csv'
        buff = self.run_sweep()
        dec_data, df, breakdown = self.parse_buffer(buff)
        self.dump_to_csv(dec_data, file)
        if plot:
            plt.plot(dec_data['volt'], dec_data['curr'])
            plt.xlabel('Voltage (V)')
            plt.ylabel('Current (A)')
            plt.show()
        print("Done!")

    def set_IV_curve_sweep(self, start, end):
        arr = np.linspace(start + 40, end + 40, 20)
        arr = np.append(arr, np.linspace(start, end, 80))
        self.set_cust_sweep('VOLT', arr, 0.001)

    # def run_IV_curve:(self, name, channels, plot=True):
    #     # file = 'C:\\Users\\ndondlinger\\Documents\\V8\\HV_failure\\IV_Curves\\' + name + '.csv'
    #     file = 'C:\\Users\\deng\\Documents\\breakdown\\' + name + '.csv'
    #     full_data = {'Channel':[],'Breakdown Voltage': [], 'Failed': []}
    #     for ch in channels:
    #         buff = self.run_sweep()
    #         dec_data, df, breakdown = self.parse_buffer(buff)
    #         full_data['Channel'].append(ch)
    #         full_data['Breakdown Voltage'].append(breakdown)
    #         if breakdown:
    #             full_data['Failed'].append(0)
    #         else:
    #             full_data['Failed'].append(1)

    def run_IV_curve(self, name, plot=True):
        # file = 'C:\\Users\\ndondlinger\\Documents\\V8\\HV_failure\\IV_Curves\\' + name + '.csv'
        # file = 'C:\\Users\\deng\\Documents\\breakdown\\' + name + '.csv'
        file = 'breakdown\\' + name + '.csv'

        buff = self.run_sweep()
        dec_data, df, breakdown = self.parse_buffer(buff)
        self.dump_to_csv(dec_data, file)
        if plot:
            plt.plot(dec_data['volt'], dec_data['curr'])
            plt.xlabel('Voltage (V)')
            plt.ylabel('Current (A)')
            plt.show()
        print("Done!")

        #for Phil's IV curve, from -300V to 1V
    def TROSA_classic_positive_negative(self, name, list, switch = True):
        if switch:
            self.dq.open_channels(self.dq.channel_str)
        self.name = name
        existing = pd.DataFrame({})
        dir = os.path.dirname(__file__)

        print(dir)

        for i in list:
            each = self.each_scan(i,switch)
            each = each[['volt','curr']]
            curr_ch = f'curr_ch{i}'
            print(existing)
            # print(curr_ch)
            # each.rename(columns = {'curr':curr_ch})
            # print(each, each.size)
            # print(existing, existing.size)
            # if existing.empty == True:
            #     existing = each
            # else:
            existing.insert(len(existing.columns), curr_ch, each['curr'].to_list())
        existing.insert(0,'volt',each['volt'].to_list())
        file = os.path.join(dir+ '/IV_curves','IV_'+name+'.csv')
        print(file)
        # file = '..\\TROSA_IV_' + name + '.csv'
        existing.to_csv(file)
        self.plot_df(existing, list)
        return existing, list



    def plot_df(self,df, list):
        #plot all wrt column 1 (volts)
        print(df)
        import matplotlib.pyplot as plt
        legend= []
        for i in list:
            plt.scatter(df['volt'], df.iloc[:,i+1].apply(lambda x: x*(1e6)), marker = '.')
            legend.append(f'Ch{i}')
        plt.xlabel('Voltage (V)', fontweight='bold')
        plt.ylabel('Current (μA)', fontweight = 'bold')
        plt.title(f'{self.name}')
        plt.legend(legend)
        # plt.xscale()
        # plt.xlim(-1, 1)
        plt.show()

        # plt.close()

        # plt.show()


    def each_scan(self, c, switch = True):
        if switch:
            self.dq.open_channels(self.dq.channel_str)
            time.sleep(2)
            self.dq.close_channels(self.dq.channels[c])
        low = -100
        high = -220
        # low = 299
        # high = -1
        sections = 2
        step = -1

        sections_pos = 3
        step_pos = -0.01
        low_pos = 1
        high_pos = -1

        # divisions_pos = (high_pos-low_pos)/sections_pos
        existing = pd.DataFrame({})
        def divide_recombine(sections, high, low, step, existing):
            divisions = (high - low) / sections
            # print(divisions)
            for i in range(sections):
                print(f'Channel {c}')
                # step = 0.5
                delay = 0.001
                self.set_sweep(mode = 'VOLT', start = low+(i*divisions), stop = low+((i+1)*divisions), step = step, delay = delay)
                new = pd.DataFrame(self.parse_buffer(self.run_sweep())).loc[2:]
                existing = pd.concat([existing, new])
            return existing
        #different sections
        # existing = divide_recombine(sections_pos, high_pos, low_pos, step_pos, divide_recombine(sections, high, low, step, existing))
        # existing = divide_recombine(sections, high, low, step, divide_recombine(sections_pos, high_pos, low_pos, step_pos, existing))
        existing = divide_recombine(sections, high, low, step, existing)

        # for i in range(sections_pos):
        return existing
if __name__ == '__main__':

    import sys
    scan_single = [0]

    scan = [0, 1, 2, 3, 4, 5, 6, 7]
    scan_rev = [7,6,5,4,3,2,1,0]

    # scan_rev = scan.reverse()
    scan_OOO_0 = [3, 5, 2, 1, 7, 4, 6, 0]
    scan_OOO_1 = [5, 7, 3, 1, 4, 6, 2, 0]

    sm = Keithley_2400()
    unit_number = 'mech_APD_1'

    for i in range(1):

        # sm.TROSA_classic_positive_negative(f'{unit_number}_forward_{i}', scan)
        sm.TROSA_classic_positive_negative(f'{unit_number}_backward_{i}', scan_single, switch = False)
        # sm.TROSA_classic_positive_negative(f'{unit_number}_rand_0_oven2_rebonded_{i}', scan_OOO_0)
        # sm.TROSA_classic_positive_negative(f'{unit_number}_rand_1_oven2_rebonded_{i}', scan_OOO_1)


    # sm.set_IV_curve_sweep()
    # sm.set_IV_curve_sweep()
    # sm.run_IV_curve(f'closed_test{n}')
    # sm.run_IV_curve('test', plot = False)

    # 0,-220,0.01,0.001)
    # else:
    # sm.run_IV_curve(sys.argv[1])
    # pass
