#!/user/bin/env python
# -*- coding: utf-8 -*-


import linguist
import jaguar

import sys

import serial
import struct
import time
import threading

import decimal
import random
import math

lock = threading.Lock()



#THIS FILE IS WHERE A ROBOT IS CREATED AND GIVEN THE TASK TO DRIVE AROUND
#REACTING TO OBSTACLES


listening = True #Listening for button presses, cliffs, wheel drops, bumper toggles
driving = False #whether the robot is in motion or not
running = True #ALWAYS TRUE, KINDA GOT STUCK WITH THIS
cliffActivated = False #If the robot has approach a cliff
clean = False
Find = False
Bump = False

_DRIVE_STRAIGHT = 150
_DRIVE_TURN = 50
_DRIVE_ROTATE_FORWARD = 150
_DRIVE_ROTATE_REVERSE = -150
_ROTATE_TIME = 2.1
_STOP_DRIVING = 0


'''
Controls the motor actions of the robot
'''
def Drive():
	global driving, listening, running, cliffActivated, clean
	listening = True
	running = True
	driving = True
	while listening:
		time.sleep(0.1)
		if driving and clean:
			lock.acquire()
			_robot.driveStraight(_DRIVE_STRAIGHT, _DRIVE_STRAIGHT)
			lock.release()
			#time.sleep(0.5)
		elif not driving and cliffActivated:
			lock.acquire()
			_robot.driveStraight(_STOP_DRIVING, _STOP_DRIVING)
			_robot.driveStraight(-(_DRIVE_STRAIGHT), -(_DRIVE_STRAIGHT)) #back up a bit, because my cliff sensors are still lagging
			#so I dont want it to fall off
			time.sleep(.2)
			lock.release()
			cliffActivated = False
			'''
		elif not driving and not Find:
			lock.acquire()
			_robot.driveStraight(_STOP_DRIVING, _STOP_DRIVING)
			lock.release()
			'''


def ListenIR():
	global listening, running, driving, Bump, clean
	LR = []
	mark = 20

	#init values
	Kp = 0.8
	Ki = 0.3
	Kd = 0.2
	errorOne = 0
	errorTwo = 0
	errorThree = 0
	distOne = 0
	distTwo = 0
	distThree = 0
	controllerOut = 0 #ut
	while 1: #implement pid controller equation in place of if statements
		lock.acquire()
		IR = _robot.readLightBump()
		lock.release()
		wallDist = IR[0] #LR [0] is right, [1] is right center
		distFront = IR[1] #right center sensor wall distance

		#error on distance and memory of previous distances
		errorThree = errorTwo
		errorTwo = errorOne
		errorOne = wallDist - mark
		proportionalT = Kp*errorOne
		integerT = Ki*0.2*(errorOne + errorTwo + errorThree)
		derivativeT = Kd*(errorOne - errorTwo)*20
		#PD equation
		controllerOut = proportionalT + derivativeT
		print controllerOut
		controllerOut = controllerOut*5
		#check for bumps
		if Bump:
			lock.acquire()
			_robot.driveStraight(-_DRIVE_STRAIGHT ,-_DRIVE_STRAIGHT )
			time.sleep(0.2)
			lock.release()
		#otherwise follow wall
		elif (controllerOut != 0) and clean:
			Find = True
			driving = False
			#wall straight ahead
			if distFront >= 10:
				Find = True
				driving = False
				lock.acquire()
				_robot.driveStraight(_DRIVE_TURN ,-_DRIVE_TURN )
				lock.release()
				time.sleep(1)
			#lost wall turn and find it
			elif(controllerOut <= -50):
				lock.acquire()
				_robot.driveStraight(30 ,120)
				lock.release()
			#otherwise just follow the wall
			else:
				lock.acquire()
				_robot.driveStraight(_DRIVE_TURN +int(controllerOut) , _DRIVE_TURN -int(controllerOut))
				lock.release()
		elif not clean:
			lock.acquire()
			_robot.driveStraight(_STOP_DRIVING, _STOP_DRIVING)
			lock.release()
		else:
			Find = False
			driving = True


'''
This method asks the robot to constantly check its bumper and wheel drop sensors.
If the robot's wheels drop, then the robot plays a song and stops running. If any of the
bumpers are hit, the robot turns depending on which bumper is hit.
'''
def ListenBumps(): #should probably change bumps to a 45 degree turn for hitting the wall its trying to follow
	global driving, listening, running, Bump
	while running: #WAS LISTENING
		lock.acquire()
		bumpState = _robot.readBumperandWheelSensors()
		lock.release()
		if bumpState == "WHEELS DROPPED" or bumpState == "BUMPED LEFT" or bumpState == "BUMPED RIGHT" or bumpState == "BUMPED LEFT AND RIGHT":
			Bump = True
			if bumpState == "WHEELS DROPPED":
				driving = False
				lock.acquire()
				_robot.playSong()
				print("IM DIFFERENT YA IM DIFFERENT")
				lock.release()
				#time.sleep(0.5)
				#running = False
		else:
			Bump = False
			'''
			elif bumpState == "BUMPED LEFT" or bumpState == "BUMPED RIGHT" or bumpState == "BUMPED LEFT AND RIGHT":
				#rotate
				variance = decimal.Decimal(random.randrange(-35,35))/100
				variance = float(variance)

				if bumpState == "BUMPED RIGHT":
					print("Rotating Left")
					lock.acquire()
					_robot.driveStraight(_DRIVE_ROTATE_REVERSE, _DRIVE_ROTATE_REVERSE)
					time.sleep(0.5)
					_robot.driveStraight(_DRIVE_ROTATE_REVERSE, _DRIVE_ROTATE_FORWARD)
					time.sleep(0.25)
					lock.release()
					#running = True


				elif bumpState == "BUMPED LEFT":
					print("Rotating Right")
					lock.acquire()
					_robot.driveStraight(_DRIVE_ROTATE_REVERSE, _DRIVE_ROTATE_REVERSE)
					time.sleep(0.5)
					_robot.driveStraight(_DRIVE_ROTATE_FORWARD, _DRIVE_ROTATE_REVERSE)
					time.sleep(0.25)
					lock.release()

				elif bumpState == "BUMPED LEFT AND RIGHT":
					#randomly chooses a direction to turn
					print("Turning Random")
					lock.acquire()
					_robot.driveStraight(_DRIVE_ROTATE_REVERSE, _DRIVE_ROTATE_REVERSE)
					time.sleep(0.5)
					lock.release()
					#running = True
				'''
			

'''
This method is constantly checking to see if the cliff sensors of the
robot are activated. The robot takes action based on any cliff sensor
being activated.
'''
def ListenCliffs():
	global driving, cliffActivated, running, clean
	while running:
		if driving:
			lock.acquire()
			cliffState = _robot.readCliffState()
			lock.release()
			if cliffState == "CLIFF ACTIVATED":
				#lock.acquire()
				#_robot.drive(_STOP_DRIVING,_STOP_DRIVING)
				#lock.release()
				print("SIKE, I WILL NOT FALL")
				cliffActivated = True
				driving = False
				clean = False
			else:
				cliffActivated = False
				driving = True



'''
This method listens to see if the CLEAN button has been pressed on the robot.
If so it changes stopDriving to true, which should alert the driver() method to
stop driving
'''
def ListenButtons():
	global listening, running, driving, clean #isCliffDetected #given access to stopDriving
	#previous = 0
	while listening: #the robot is listening for button clicks
			lock.acquire()
			a = _robot.readButton(jaguar.Buttons['_CLEAN']) #boolean for if the button has been clicked
			lock.release()
			if a:
				clean = not clean
				#print("CLEAN BUTTON TOGGLED." + "  " + str(driving))



_robot = jaguar.Jaguar() #initilizes robot by setting it in passive and safe mode
time.sleep(.01) #process time

_robot.changeState(jaguar.States['_FULL'])

t1 = threading.Thread(target = Drive) #first thread for listening
t2 = threading.Thread(target = ListenCliffs) #second thread for driving
t3 = threading.Thread(target = ListenBumps)
t4 = threading.Thread(target = ListenButtons)
t5 = threading.Thread(target = ListenIR)


print("START")
#t2.start() #starts the second thread
t3.start()
t5.start()
t4.start()
t1.start() #start the first thread
