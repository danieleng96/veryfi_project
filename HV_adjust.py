import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import APD_breakdown.SQL_server as sql

# df = pd.read_csv(r'C:\Users\deng\Desktop\trosa_line\conversion_table_v8_apa.csv')
# apa_t = df['APA_t']
# v8_t = df['V8_t(real)']
# x_s = np.linspace(50,130,1000)
# size = np.size(x_s)
# print(x_s)
# plt.plot(apa_t,v8_t, marker = '*', linestyle = None)
# for deg in range(8):
#         # print(deg)
#         fit = np.polyfit(apa_t, v8_t, deg, rcond=None, full=False)
#         print(fit)
#         y = np.zeros(1000)
#         list=[]
#         for n in range(deg):
#             list.append(n)
#             term = np.power(x_s,deg-n)*fit[n]
#             y = y + term
#         # if deg < 4:
#         plt.plot(x_s,y, marker = '.', linestyle = 'None', label = f'Polynomial {deg}')
# plt.plot(x_s, 0.9608*x_s - 35.348, marker = None, linestyle = '-')
# plt.ylim(0,95)
# plt.legend()
# plt.show()

# read temperature each from TROSA
hv =
remove_slope = 'reg_access -w -a 44c0010c -d 0'
set_HV = f'v8 monitor --set_hv_setpoint 0 {hv}'

'''
Edited by Daniel Eng

Reads original calibration file for V16 unit

The optical power target is obtained by looking at the initial
output power after turned on for a while for each channel

'''


import argparse
from datetime import datetime
import glob
import io
import numpy as np
import os
import pandas as pd
import re
import sys
import time
import csv
import pyvisa

from velaplatform.velarray.velarray import velarray_v8_a0

v8a0 = velarray_v8_a0(ip_addr='192.168.1.100', port='0x1080')


import devices.Omega_Platinum as Omega_Platinum
import devices.ThorlabsPM100USB as ThorlabsPM100USB

PICK_DEVICES = True

THORLABS_PM100USB_DEVICE_NAME = 'USB0::4883::32882::1907345::0::INSTR'
ID_PRODUCT = '32882'

OMEGA_PLATNIUM_DEVICE_PATH = '/dev/ttyACM0'
OMEGA_SERIAL_STRING = 'ttyACM'
OMEGA_CHANNEL = 110

TOTAL_LASERS = 8

TEMPERATURE_TOLERANCE = 50
OPTICAL_POWER_TOLERANCE = 0.001

power_all_list = []


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getCalibration(filename):
    cal_dict = []
    for i in range(0, 8):
        file = open(filename)
        file_reader = csv.DictReader(file, delimiter=",")
        each_channel = []
        for line in file_reader:
            if int(line['Channel']) == i and int(line['Power Level']) == 15:
                each_channel.append({'Channel': line['Channel'],
                                     'Power Level': line['Power Level'],
                                     'Temperature': line['Temperature'],
                                     'Calibrated VBias': line['Bias']})
                                 #    'Initial Optical Output': line['Optical Power in mW']})
        cal_dict.append(each_channel)
        print(each_channel)
    return cal_dict


'''
cal_dict = getCalibration('V8_LD1_power_level_table.csv')
for channel in range(0,4):
    for i in cal_dict[channel]:
        if i['Channel'] == str(channel) and i['Power Level'] == str(15):
            print(i['Calibrated VBias'])
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('calibrationFile', help='Required. Specify the calibration file.')
    args = parser.parse_args()

    # Because the worst starting point is 0 or 8192. My step size is 5 per v-bias
    # so 1640 tries will cover the entire 8192 range.
    MAXIMUM_TRIES = 200
    DWELL_TIME = 240  # seconds to be used on conjunction with time.sleep(1)

    MAX_V_BIAS_COUNTS = 8192  # Maximum value at which v-bias is setable. Warning: Will likely throw an eye-safety fault.

    vBiasesFromPowerTable = []
    opticalPowersFromPowerTable = []
    power_all = 0

    if args.calibrationFile is not None:
        calibrationData = getCalibration(args.calibrationFile)

    numberOfCalibrationEntries = len(calibrationData)

    vBiasesForExtrapolation = [[]] * numberOfCalibrationEntries
    opticalPowersForExtrapolation = [[]] * numberOfCalibrationEntries

    #   calibrationData = getCalibration('V8_LD1_power_level_table.csv')

    # This will get the actual initial output power for each channel
    InitialOpticalOutput = [21.3,20.5,22.1,22.6,21.4,20.8,19.6,21.5]
    for channel in range(0, 8):
        print(channel)
        calibrationData[channel][0]['Initial Optical Output'] = InitialOpticalOutput[channel]

    for iter, calibrationEntry in enumerate(calibrationData):
        eachChannel = int(calibrationEntry[0]['Channel'])
        eachCalibratedVBias = round((float(calibrationEntry[0]['Calibrated VBias'])*16383/8))
        eachTargetOpticalOutput = float(calibrationEntry[0]['Initial Optical Output'])

        attenuation = 20

        if float(eachCalibratedVBias) >= 0 and float(eachCalibratedVBias) < MAX_V_BIAS_COUNTS:
            vBiasesForExtrapolation[iter] = [eachCalibratedVBias]
            opticalPowersForExtrapolation[iter] = [eachTargetOpticalOutput]

        else:
            print(calibrationEntry)
            print('This entry contains an invalid v-bias value. All values have been converted to base-10.')
            print('Terminated.')
            exit(-1)
    try:
        defaultDevice = None
        if PICK_DEVICES:
            devicesList = glob.glob(('/dev/ttyACM?'))

            print(
                'Select the device number which corresponds to the ' + bcolors.BOLD + 'Omega temperature device: ' + bcolors.ENDC)
            for itemize, eachResource in enumerate(devicesList):
                if OMEGA_SERIAL_STRING in eachResource:
                    print('%d. %s [%sENTER%s = DEFAULT]' % (itemize, eachResource, bcolors.OKGREEN, bcolors.ENDC))
                    defaultDevice = itemize
                else:
                    print('%d. %s' % (itemize, eachResource))

            userInput = input(
                'Enter a number or press ' + bcolors.OKGREEN + 'ENTER' + bcolors.ENDC + ' to select the default device if indicated.')
            if userInput == '' or userInput.isnumeric() == False:
                userInput = defaultDevice

            userInput = int(userInput)
            omega = Omega_Platinum.Omega_Platinum(devicesList[userInput])

        else:
            omega = Omega_Platinum.Omega_Platinum(OMEGA_PLATNIUM_DEVICE_PATH)

        pass
    except Exception as e:
        print(e)
        print(
            'Warning! Cannot communicate with the Omega temperature device. The script will likely crash as it progresses.')

    try:
        defaultDevice = None
        if PICK_DEVICES:
            rm = pyvisa.ResourceManager()
            resources = rm.list_resources()

            print('Select the device number which corresponds to the %sThorLabs PM100USB%s: ' % (
            bcolors.OKGREEN, bcolors.ENDC))
            for itemize, eachResource in enumerate(resources):
                if ID_PRODUCT in eachResource:
                    print('%d. %s [%sENTER%s = DEFAULT]' % (itemize, eachResource, bcolors.OKGREEN, bcolors.ENDC))
                    defaultDevice = itemize
                else:
                    print('%d. %s' % (itemize, eachResource))

            userInput = input('Enter a number or press %sENTER%s to select the default device if indicated.' % (
            bcolors.OKGREEN, bcolors.ENDC))
            if userInput == '' or userInput.isnumeric() == False:
                userInput = defaultDevice

            userInput = int(userInput)
            powerMeter = ThorlabsPM100USB.ThorlabsPM100USB(resources[userInput])
        else:
            powerMeter = ThorlabsPM100USB.ThorlabsPM100USB(THORLABS_PM100USB_DEVICE_NAME)

        powerMeter.set_wavelength(905)
        powerMeter.set_attenuation_level(attenuation)
        print('Reported settings:')
        print('    Wavelength settings: %s\r' % powerMeter.get_wavelength())
        print('    Attenuation level: %s\r' % powerMeter.get_attenuation_level())

        result = v8a0.subcomponents['monitor'].get_system_temperature()
        print('System temperature: %f' % result)
        result = v8a0.subcomponents['he_scan_ctrl'].get_scan_fault_allow_status()
        print(result)

        v8a0.subcomponents['he_scan_ctrl'].set_scan_fault_allow_status(True)
        v8a0.subcomponents['fault'].clear_eye_safety_faults()

        print('Mirror scanning configured to be off with lasers still powered.')
        print('Nothing will be done to reenable eye safety faults when this script ends or anytime in between.')
        print('Please exercise eye-safety caution!')

        v8a0.subcomponents['calmode_ctrl'].set_power_mode('fixed')
        print('Power mode set to fixed.')

        vBiasValues = [[]] * TOTAL_LASERS

        timestamp = datetime.now().strftime('%y-%m-%d-%H%M%S')
        filename = 'v_bias_search_results_' + timestamp + '.csv'
        print('The file %s will be created.' % filename)

        header = 'Date, Time, Channel, Calibrated VBias, Cutoff Vbias, Measured Vbias, Initial Optical Output,' \
                 'Is Degraded Vbias, Degraded Optical Output (mW), Percent Degradation, TEC Temp, LEC1 Temp All Channels,' \
                 'LEC2 Temp All Channels, LEC1 Temp Single Channel, LEC2 Temp Single Channel, Is Power Degraded,Tries\n'
        with open(filename, 'w') as writer:
            writer.write(header)

        # Make file to monitor temperature and power while PL15 is on

        filename_monitor = 'v_bias_search_results_'+timestamp+'monitor'+'.csv'
        header_monitor = 'Date, Time, Omega Temp (C), LEC1 Temp (C), LEC2 Temp (C), Optical Power (mW)'
        with open(filename_monitor, 'w') as writer:
            writer.write(header)

        while True:

#            for entryIter, eachCalibratedEntry in enumerate(calibrationData):
            for eachCalibratedEntry in calibrationData :
                eachChannel = int(eachCalibratedEntry[0]['Channel'])
                eachCalibratedVBias = round((float(eachCalibratedEntry[0]['Calibrated VBias'])*16383/8))
                eachCutoffVBias = round(eachCalibratedVBias+500)
                eachOpticalOutput = float(eachCalibratedEntry[0]['Initial Optical Output'])
                print(eachCalibratedVBias)


                # Make sure Vbias is original value
                setBiasArgs = '0,%d,15,%d' % (eachChannel, eachCalibratedVBias)
                tArgs = argparse.Namespace(set_bias=setBiasArgs, export=None, set_power=None, set_lp=None,
                                           set_boot=None)
                v8a0.subcomponents['pwr_ctrl'].run_cli(tArgs)

                v8a0.subcomponents['pwr_ctrl'].set_trigger_state_lcp(0, False)
                v8a0.subcomponents['pwr_ctrl'].set_trigger_state(0, eachChannel, True)
                v8a0.subcomponents['pwr_ctrl'].set_single_channel_pwrlvl(0, eachChannel, 15)
                time.sleep(1)

                # Get optical output before adjusting VBias
                is_pwr_degraded = 'No'
                try:
                    degraded_optical_pwr = powerMeter.read_power_level() * 1000
                    percent_degradation = round(((eachOpticalOutput - degraded_optical_pwr) / eachOpticalOutput * 100),2)
                except ZeroDivisionError:
                    percent_degradation = 100
                    is_pwr_degraded = 'Yes'
                    print('\nChannel stopped working')


                lTemp = omega.get_temperature(OMEGA_CHANNEL)
                LECT1_single_on = v8a0.subcomponents['monitor'].get_trosa_temperature(0)


                print("\nTEC Temp: %d, LEC1 Temp: %d"% (lTemp,LECT1_single_on))


                if percent_degradation > 10.5:
                    print("\nOutput power for channel %d decreased more than 10 percent. \n" %eachChannel)



                if len(opticalPowersForExtrapolation[eachChannel]) > 5:
                    opticalPowersForExtrapolation[eachChannel].pop(0)

                if len(vBiasesForExtrapolation[eachChannel]) > 5:
                    vBiasesForExtrapolation[eachChannel].pop(0)

                if len(opticalPowersForExtrapolation[eachChannel]) == 1:
                    setBiasArgs = '0,%d,15,%d' % (eachChannel, vBiasesForExtrapolation[eachChannel][0] + 50)
                    tArgs = argparse.Namespace(set_bias=setBiasArgs, export=None, set_power=None, set_lp=None,
                                               set_boot=None)
                    v8a0.subcomponents['pwr_ctrl'].run_cli(tArgs)
                    time.sleep(1)
                    opticalPowerLevel = powerMeter.read_power_level() * 1000
                    opticalPowersForExtrapolation[eachChannel].append(opticalPowerLevel)
                    vBiasesForExtrapolation[eachChannel].append(vBiasesForExtrapolation[eachChannel][0] + 50)

                try:
                    z = np.polyfit(opticalPowersForExtrapolation[eachChannel], vBiasesForExtrapolation[eachChannel], 1)
                    f = np.poly1d(z)
                    biasIter = f(eachOpticalOutput)
                    if not (biasIter >= 0 and biasIter <= MAX_V_BIAS_COUNTS):
                        biasIter = eachCalibratedVBias

                    biasIter = int(biasIter)
                    print('\nChannel %d. Best v-bias guess: [%d]' % (eachChannel, biasIter))

                except ValueError:
                    continue

                tries = 0
                vBiasIsDegraded = 'No'

                print(
                    'Calibrated VBias = %.2f, Calibrated Output Power = %.2f, Current Output Power = %.2f, Percent Degradation =%.2f ' % (
                    eachCalibratedVBias, eachOpticalOutput, degraded_optical_pwr, percent_degradation))

                while tries < MAXIMUM_TRIES:

                    opticalPowerLevel = round((powerMeter.read_power_level() * 1000),2)
                    print(
                        'Channel %d: Target optical output: %.2f mW. Current optical output: %.2f mW. Current V-bias: [%d]. Try %d of %d\r' % (
                        eachChannel, eachOpticalOutput, opticalPowerLevel, biasIter, tries, MAXIMUM_TRIES), end='')
                    if opticalPowerLevel < eachOpticalOutput:
                        biasIter += 5
                    elif opticalPowerLevel > eachOpticalOutput:
                        biasIter -= 5

                    if (opticalPowerLevel >= eachOpticalOutput - (eachOpticalOutput * OPTICAL_POWER_TOLERANCE)) and \
                            (opticalPowerLevel <= eachOpticalOutput + (eachOpticalOutput * OPTICAL_POWER_TOLERANCE)):
                        print('Channel %d: Found v-bias [%d]!' % (eachChannel, biasIter))
                        opticalPowersForExtrapolation[eachChannel].append(opticalPowerLevel)
                        vBiasesForExtrapolation[eachChannel].append(biasIter)
                        break

                    if biasIter >= MAX_V_BIAS_COUNTS or biasIter <= 0:
                        print('V-Bias [%d] fell out of bounds.' % biasIter)
                        print('Breaking out of this loop iteration for channel %d...' % eachChannel)

                        break

                    # Set vbias as new found Vbias
                    setBiasArgs = '0,%d,15,%d' % (eachChannel, biasIter)
                    tArgs = argparse.Namespace(set_bias=setBiasArgs, export=None, set_power=None, set_lp=None,
                                               set_boot=None)
                    v8a0.subcomponents['pwr_ctrl'].run_cli(tArgs)

                    time.sleep(1)
                    tries += 1

                # Make sure Vbias is original value
                setBiasArgs = '0,%d,15,%d' % (eachChannel, eachCalibratedVBias)
                tArgs = argparse.Namespace(set_bias=setBiasArgs, export=None, set_power=None, set_lp=None,
                                           set_boot=None)
                v8a0.subcomponents['pwr_ctrl'].run_cli(tArgs)

                if biasIter >= eachCutoffVBias:
                    vBiasIsDegraded = 'Yes'

                if tries >= MAXIMUM_TRIES:
                    #                    vBiasIsDegraded = 'N/A'
                    #                    biasIter = 'N/A'
                    #                    opticalPowerLevel = 'N/A'
                    print('Tried unsuccessfully to set the v-bias %d times. Stopped for channel %d.' % (
                    tries, eachChannel))

                lTemp = omega.get_temperature(OMEGA_CHANNEL)

                with open(filename, 'a') as writer:
                    lDate = datetime.now().strftime('%m-%d-%y')
                    lTime = datetime.now().strftime('%H%M%S')
                    writeThis = '{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} \n'.format(lDate, lTime,
                                                                                               eachChannel,
                                                                                               eachCalibratedVBias,
                                                                                               eachCutoffVBias,
                                                                                               biasIter,
                                                                                               eachOpticalOutput,
                                                                                               vBiasIsDegraded,
                                                                                               round(degraded_optical_pwr,2),
                                                                                               percent_degradation,
                                                                                               lTemp,
                                                                                               LECT1_single_on,
                                                                                               is_pwr_degraded,
                                                                                               tries)
                    writer.write(writeThis)

                # let TROSA get back into equilibrium for next channel
                v8a0.subcomponents['pwr_ctrl'].set_trigger_state_lcp(0, False)
                print("Waiting for TROSA to cool off for next channel \n")
                time.sleep(30)
            # Turn on all lasers and set PL15.
            v8a0.subcomponents['pwr_ctrl'].set_trigger_state_lcp(0, True)
            for iter in range(0, TOTAL_LASERS):
                v8a0.subcomponents['pwr_ctrl'].set_trigger_state(0, iter, True)
                v8a0.subcomponents['pwr_ctrl'].set_single_channel_pwrlvl(0, iter, 15)

            print('All lasers are enabled and set to PL=15.')

            for countSeconds in range(10, 0, -1):
                print('Sleeping for %d seconds...\r' % (
                    countSeconds), end='')
                time.sleep(60)
                LECT1_All_On = v8a0.subcomponents['monitor'].get_trosa_temperature(0)
                lTemp = omega.get_temperature(OMEGA_CHANNEL)
                lDate = datetime.now().strftime('%m-%d-%y')
                lTime = datetime.now().strftime('%H%M%S')
                power_all = powerMeter.read_power_level() * 1000
                print("LEC1 T: %d" % (LECT1_All_On))
                with open(filename_monitor,'a') as writer:
                    writeThis1 = '{}, {}, {}, {}, {}\n'.format(lDate,lTime,lTemp,LECT1_All_On,power_all)
                    writer.write(writeThis1)


            # Turn off lasers and keep that way for a minute for LEC temp to stabilize
            for iter in range(0, TOTAL_LASERS):
                v8a0.subcomponents['pwr_ctrl'].set_trigger_state_lcp(0, False)
            for countSeconds in range(180,0,-1):
                time.sleep(1)
                print('Lasers turned off for measurement. Sleeping for %d seconds \r'%(countSeconds),end='')

    except IOError as e:
        print(
            'Unable to communicate with either the V8 sensor, the Omega temperature controller, or the ThorLabs PM100USB.')
        print('Please check your connections/power to devices and try again.')
        print(e)


if __name__ == '__main__':
    main()





