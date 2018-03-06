#!/user/bin/env python
# -*- coding: utf-8 -*-
import serial
import struct 
import time

# The Linguist handles raw communication and messaging with the iRobot 
class Linguist:

    _PORT = '/dev/ttyUSB0' 
    _BAUDRATE = 115200
    _TIMEOUT= 1

    serialConnectionM = None; #the serial connection with the robot

    '''
    On initilization of Linguist, a serial connection is established
    '''
    def __init__(self): 
        self.serialConnection() 

    '''
    Sets the serial connection with the robot
    '''
    def serialConnection(self):
        self.serialConnectionM = serial.Serial(self._PORT, baudrate = self._BAUDRATE, timeout = self._TIMEOUT)        
        print("Linguist initialized. Serial Connection established.")
    '''
    Closes the serial connection with the robot
    '''
    def close(self):
        self.serialConnectionM.close()

    '''
    Sends commands to the robot. Is set to recieve an integer or an array of integers. 
    '''
    def sendCommand(self, command):
        if isinstance(command, list): #first checks if command is an array
            #if so, we know that the array is full of the bytes for the drive commmand, so we send each byte of the array
           
            if len(command) > 5:
                cmd =''
                for i in range(0,len(command)):
                    cmd += chr(command[i])

                return self.serialConnectionM.write(cmd)
            else:
                return self.serialConnectionM.write(chr(command[0]) + chr(command[1]) + chr(command[2]) + chr(command[3]) + chr(command[4]))

        #otherwise the command is just 1 integer
        #print(command)
        cmd = chr(command) #convert command 
        return self.serialConnectionM.write(cmd) #write command to robot
        
    '''
    Returns data read from robot. The paramter data serves as the number of bytes wanting to be read
    '''
    def readData(self, data): 
        return self.serialConnectionM.read(data)




