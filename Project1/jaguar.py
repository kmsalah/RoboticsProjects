#!/user/bin/env python

import linguist
import serial
import struct
import time


_SENSOR_DATA_REQUEST = 142
_BUTTON_PACKET_ID = 18
_DRIVE = 137

Buttons = {
	#button codes	
	"_CLOCK": 0x80,
	"_SCHEDULE": 0x40,
	"_DAY": 0x20,
	"_HOUR": 0x10,
	"_MINUTE": 0x08,
	"_DOCK": 0x04,
	"_SPOT": 0x02,
	"_CLEAN": 0x01
}

States = {
	#STATE CODES 
	"_START": 128,
	"_SAFE": 128,
	"_PASSIVE": 131,
	"_RESET": 7,
	"_STOP": 173,
	"_FULL": 132
}



#The Jaguar controls the actions of the iRobot using the Linguist serial communcation interface
class Jaguar: 

	COMPLEMENT = {'1': '0', '0': '1'} #used by the getTwosComp method 

	linguistM = None 

   	stateM= None
        

	'''
	Takes in an integer and returns an array containing two bytes in decimal form. 
	This method takes an integer, converts it into two's complement, converts into hex, divides that 4 character hex 
	numbers into two 2 character hex numbers. Those two numbers are converted into decimal form and packed into an array
	that is then returned.
	'''
	def getBytes(self, x):
		#if x is positive, just convert to binary, divide in half, convert to int form, pack two ints up 
	    if(x>=0):
	        binaryString = self.getBinaryString(x) #getting a 2 byte string
	        #were assuming that the binary string is only 16 bits because that's what it should return
	        firstHalf = binaryString[0:8] #firstHalf = binaryString from 0 index to 7 index
	        secondHalf = binaryString[8:] #secondHalf = binaryString from 8 index to the end


	        firstDec = int(firstHalf, 2) #convert first half from binary String into an int
	        secondDec = int(secondHalf,2) #same idea
	       	
	       	pack = [] #create the array
	       	#do some packing
	       	pack.append(firstDec)
	       	pack.append(secondDec)
	       	return pack 
	    else:
	    	#else if the int is negative, we'll need to do a proper Two's comp conversion 
	       	binaryString = self.getTwosComp(x, 16) #returns the two's comp binary string

	       	#everything else is the same as above
	       	firstHalf = binaryString[0:8]
	       	secondHalf = binaryString[8:]

	       	firstDec = int(firstHalf, 2)
	       	secondDec = int(secondHalf,2)

	       	pack = []
	       	pack.append(firstDec)
	       	pack.append(secondDec)
	       	print(pack)
	       	return pack


	def getBinaryString(self, x):
		string = bin(x)
		binString= string[2:] #this gets rid of the "0b" at the beginning thats added
	    #now I have a  binary string, but I need it to be 16 bits long

		neededBits = 16 - len(binString) 
		addOn = ""
		#however many bits are needed to make the final string == 16 bits, add those to a string
		for i in range(0, neededBits):
			addOn+='0'
		#add those extra needed bits to the beginning
		return addOn + binString

	'''
	Converts a number to the Two's Complement binary string equivalent in the desired number of bits
	'''
	def getTwosComp(self, number, size_in_bits):
		#great method found online for getting 2's comp
		#https://michaelwhatcott.com/a-few-bits-of-python/
	    if number < 0:
	        return self.compliment(bin(abs(number) - 1)[2:]).rjust(size_in_bits, '1')
	    else:
	        return bin(number)[2:].rjust(size_in_bits, '0')

	'''
	Helper method for getTwosComp
	'''
	def compliment(self,value):
	    return ''.join(self.COMPLEMENT[x] for x in value)


	'''
	Initializes an instance of Jaguar
	'''
   	def __init__(self):
		print("iRobot.Jaguar_1.0 created!")
   		self.linguistM = linguist.Linguist() #creates a Linguist interface to communicate with iRobot
   		self.changeState(States['_START']) #changes state to start
   		self.changeState(States['_PASSIVE']) #then change state to passive
		print("Click Clean button to start the robot")
   	
   	'''
	Changes the state of the iRobot. Changes the member variable of the robot to the right state and 
	sends a command to the robot to change the actual state of the iRobot.
   	'''
	def changeState(self, newState):
		self.stateM = newState #change state variable to right code
		self.linguistM.sendCommand(newState) #send command to change
		if(newState == "_STOP"): #if the commmand was to stop
			self.linguistM.close() #close the connection
		time.sleep(1) #wait a little for things to process

	'''
	This method takes in a button hex code and returns true or false depending on if the  button has been clicked.
	First the method sends the correct Sensor Data Request code and Button Packet ID to have the robot send pack 
	bytes specifying if the button has been hit. The data is unpacked and checked to see if the code is the same as 
	the button code paramter. 
	'''
	def readButton(self, button):
		#self.changeState(States._START) #why is this the only way
		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST) #send data request
		self.linguistM.sendCommand(_BUTTON_PACKET_ID) #send corresponding button packet ID

		data = self.linguistM.readData(1) #reads 1 byte from serial port, is the hex code

		if len(data) == 1:
			data = struct.unpack('B', data)[0]  #converts to decimal 
			return bool(data & button) 
		else:
			return False


	'''
	Commands the robot to drive at a certain speed and radius
	'''
	def drive(self,velocity, radius):
		vPack = self.getBytes(velocity) #get an array with the high velocity byte and low velocity byte
		rPack = self.getBytes(radius) #get an array with the high radius byte and low radius byte
		self.changeState(States['_FULL'])
		drivePack = [_DRIVE] #create an array and the first element is set to the drive command
		drivePack.append(vPack[0]) #add te high velocity byte
		drivePack.append(vPack[1]) #add the low velocity byte
		drivePack.append(rPack[0]) #add the high radius byte
		drivePack.append(rPack[1]) #add the low radius byte

		self.linguistM.sendCommand(drivePack) #send the array with the 5 values to be send to the robot




		


	


    	
