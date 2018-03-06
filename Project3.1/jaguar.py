#!/user/bin/env python

import linguist
import serial
import struct
import time
import math


_SENSOR_DATA_REQUEST = 142
_BUTTON_PACKET_ID = 18
_BUMP_WHEEL_PACKET_ID = 7

_CLIFF_LEFT_PACKET_ID = 9
_CLIFF_FRONT_LEFT_PACKET_ID = 10
_CLIFF_FRONT_RIGHT_PACKET_ID = 11
_CLIFF_RIGHT_PACKET_ID = 12

_DRIVE = 137
_DRIVE_STRAIGHT = 145

_INFRARED_CHAR_OMNI = 17
_INFRARED_CHAR_LEFT = 52
_INFRARED_CHAR_RIGHT = 53

_LIGHT_BUMP = 45
_LIGHT_BUMP_LEFT_SIGNAL = 46
_LIGHT_BUMP_FRONT_LEFT_SIGNAL = 47
_LIGHT_BUMP_CENTER_LEFT_SIGNAL = 48
_LIGHT_BUMP_CENTER_RIGHT_SIGNAL = 49
_LIGHT_BUMP_FRONT_RIGHT_SIGNAL = 50
_LIGHT_BUMP_RIGHT_SIGNAL = 51


Sounds = {
	"_CREATE_SONG": 140,
	"_PLAY_SONG": 141,
	"_TWO_CHAINZ": 1, #song number
	"_NUM_NOTES": 7,
	"_LETTER_C": 96,
	"_LETTER_B": 95,
	"_LETTER_E": 88,
	"_LETTER_A": 93,
	"_LETTER_F": 89,
	"_DOTTED_QUARTER_NOTE": 51,
	"_HALF_NOTE": 68,
	"_DOTTED_HALF_NOTE": 102,
	"_QUARTER_NOTE": 24,
	"_EIGHTH_NOTE": 12
}


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
   		#self.changeState(States['_STOP'])
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

	def readBumperandWheelSensors(self):
		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_BUMP_WHEEL_PACKET_ID)
		data = self.linguistM.readData(1)

		if len(data) == 1:
			data = struct.unpack('B', data)[0]
			if data > 3: #if its greater than 3, that means that any combo containing a wheel drop is true
				return "WHEELS DROPPED"
			elif data == 3:
				return "BUMPED LEFT AND RIGHT"
			elif data == 2:
				return "BUMPED LEFT"
			elif data == 1:
				return "BUMPED RIGHT"
			elif data == 0:
				return "NOTHING"

	def readCliffState(self):
		result = 0

		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_CLIFF_FRONT_LEFT_PACKET_ID)
		data = self.linguistM.readData(1)
		if len(data) == 1:
			data = struct.unpack('B', data)[0]
			result = result + data
		#time.sleep(0.0015)
		if result > 0:
			return "CLIFF ACTIVATED"

		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_CLIFF_FRONT_RIGHT_PACKET_ID)
		data = self.linguistM.readData(1)
		if len(data) == 1:
			data = struct.unpack('B', data)[0]
			result = result + data
		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_CLIFF_LEFT_PACKET_ID)

		data = self.linguistM.readData(1)
		if len(data) == 1:
			data = struct.unpack('B', data)[0]
			result = result + data
		#time.sleep(0.0015)
		if result > 0:
			return "CLIFF ACTIVATED"


		#time.sleep(0.0015)
		if result > 0:
			return "CLIFF ACTIVATED"

		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_CLIFF_RIGHT_PACKET_ID)
		data = self.linguistM.readData(1)
		if len(data) == 1:
			data = struct.unpack('B', data)[0]
			result = result + data
		#time.sleep(0.0015)

		if result > 0:
			return "CLIFF ACTIVATED"
		else:
			return "CLIFF NOT ACTIVATED"



	def playSong(self):
		songPack = []
		songPack.append(Sounds['_CREATE_SONG'])
		songPack.append(Sounds['_TWO_CHAINZ'])
		songPack.append(Sounds['_NUM_NOTES']) #7 notes

		songPack.append(Sounds['_LETTER_C'])
		songPack.append(Sounds['_DOTTED_QUARTER_NOTE'])

		songPack.append(Sounds['_LETTER_B'])
		songPack.append(Sounds['_HALF_NOTE'])

		songPack.append(Sounds['_LETTER_E'])
		songPack.append(Sounds['_QUARTER_NOTE'])

		songPack.append(Sounds['_LETTER_A'])
		songPack.append(Sounds['_QUARTER_NOTE'])

		songPack.append(Sounds['_LETTER_A'])
		songPack.append(Sounds['_QUARTER_NOTE'])

		songPack.append(Sounds['_LETTER_F'])
		songPack.append(Sounds['_DOTTED_QUARTER_NOTE'])

		songPack.append(Sounds['_LETTER_E'])
		songPack.append(Sounds['_EIGHTH_NOTE'])

		self.linguistM.sendCommand(songPack)

		self.linguistM.sendCommand(Sounds["_PLAY_SONG"]) #
		self.linguistM.sendCommand(Sounds["_TWO_CHAINZ"])

	'''
	Commands the robot to drive at a certain speed and radius
	'''
	def drive(self,velocity, radius):
		vPack = self.getBytes(velocity) #get an array with the high velocity byte and low velocity byte
		rPack = self.getBytes(radius) #get an array with the high radius byte and low radius byte
		#self.changeState(States['_FULL'])
		drivePack = [_DRIVE] #create an array and the first element is set to the drive command
		drivePack.append(vPack[0]) #add te high velocity byte
		drivePack.append(vPack[1]) #add the low velocity byte
		drivePack.append(rPack[0]) #add the high radius byte
		drivePack.append(rPack[1]) #add the low radius byte

		self.linguistM.sendCommand(drivePack) #send the array with the 5 values to be send to the robot

	def driveStraight(self, leftV, rightV):
		lPack = self.getBytes(leftV)
		rPack = self.getBytes(rightV)
		#self.changeState(States['_FULL'])
		drivePack = [_DRIVE_STRAIGHT]
		drivePack.append(lPack[0]) #add te high velocity byte
		drivePack.append(lPack[1]) #add the low velocity byte
		drivePack.append(rPack[0]) #add the high radius byte
		drivePack.append(rPack[1]) #add the low radius byte

		self.linguistM.sendCommand(drivePack)


	def readLightBump(self):
		LR = []
		center = 0
		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_LIGHT_BUMP_RIGHT_SIGNAL)
		data = self.linguistM.readData(2)
		if len(data) == 2:
			data = struct.unpack('>H', data)[0]
		data = math.sqrt(data)
		LR.append(float(data))

		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_LIGHT_BUMP_CENTER_LEFT_SIGNAL)
		data = self.linguistM.readData(2)
		if len(data) == 2:
			data = struct.unpack('>H', data)[0]
		center += data

		self.linguistM.sendCommand(_SENSOR_DATA_REQUEST)
		self.linguistM.sendCommand(_LIGHT_BUMP_CENTER_RIGHT_SIGNAL)
		data = self.linguistM.readData(2)
		if len(data) == 2:
			data = struct.unpack('>H', data)[0]
		center += data
		center = center * 0.5
		center = math.sqrt(center)
		LR.append(center)
		return LR
