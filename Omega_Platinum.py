# -*- coding: utf-8 -*-
'''
Created on Wed Aug  13 21:26:58 2018

@author: Jack Schoenduve
Omega Engineering Platinum sensor
'''

import time
import serial

class Omega_Platinum:
    def __init__(self, serial_port = 'COM3'):
        self.port = serial_port
        self.ser = serial.Serial(self.port, 115200, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
        print(self.ser)
        self.ser.close()
        if self.ser.is_open == False:
            self.ser.open()

    def get_temp(self, channel=110):
        ''' read channel for temperature data G112+9999.0 '''
        #split_str = []
        temp = 0
        cmd = str.encode('*G' + str(channel) + '\r')
        self.ser.write(cmd)
        time.sleep(1)
        if self.ser.in_waiting > 0:
            readBytes = self.ser.inWaiting()
            #print('Read bytes:{}'.format(readBytes))
            read_buffer = self.ser.read(readBytes)

            #print('Read Buffer is:{}'.format(read_buffer))
            if len(read_buffer) > 0:
                #read_temp = str.decode(read_buffer)
                read_temp = read_buffer[5:10]
                #read_temp = str(read_buffer)
                #read_temp = read_temp.strip('\r\n\0')
                #print('Stripped read_temp:{}'.format(read_temp))
                #split_str = read_temp.split('+')
                #temp = split_str[1]
                #print('Temp:{}'.format(temp))
                temp = float(read_temp)
        return temp

    def set_temp(selfself, channel = 110):
        cmd = str.encode('')

if __name__ == '__main__':
    for i in range(10):
        print(Omega_Platinum().get_temp())
        time.sleep(5)
