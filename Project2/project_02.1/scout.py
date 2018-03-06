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

lock = threading.Lock()



#THIS FILE IS WHERE A ROBOT IS CREATED AND GIVEN THE TASK TO DRIVE AROUND 
#REACTING TO OBSTACLES


listening = True #Listening for button presses, cliffs, wheel drops, bumper toggles
driving = False #whether the robot is in motion or not
running = True #ALWAYS TRUE, KINDA GOT STUCK WITH THIS
cliffActivated = False #If the robot has approach a cliff

_DRIVE_STRAIGHT = 200
_DRIVE_ROTATE_FORWARD = 150
_DRIVE_ROTATE_REVERSE = -150
_ROTATE_TIME = 2.1
_STOP_DRIVING = 0


'''
Controls the motor actions of the robot
'''
def Drive():
	global driving, listening, running, cliffActivated
	running = True
	#driving = True
	while 1:
		if driving:
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
		elif not driving:
			lock.acquire()
			_robot.driveStraight(_STOP_DRIVING, _STOP_DRIVING)
			lock.release()
			#time.sleep(0.5)
			#time.sleep(0.5)
			#if not running:
				#break
		

'''
This method asks the robot to constantly check its bumper and wheel drop sensors. 
If the robot's wheels drop, then the robot plays a song and stops running. If any of the 
bumpers are hit, the robot turns depending on which bumper is hit.
'''

def ListenBumps():
	global driving, listening, running	
	while running: #WAS LISTENING
		#time.sleep(.15)
		if driving:
			lock.acquire()
			bumpState = _robot.readBumperandWheelSensors()
			lock.release()
			if bumpState == "WHEELS DROPPED" or bumpState == "BUMPED LEFT" or bumpState == "BUMPED RIGHT" or bumpState == "BUMPED LEFT AND RIGHT":
				#running = False
				if bumpState == "WHEELS DROPPED":
					driving = False	
					lock.acquire()
					_robot.playSong()
					print("IM DIFFERENT YA IM DIFFERENT")
					lock.release()
					#time.sleep(0.5)
					#running = False	
					
			
				elif bumpState == "BUMPED LEFT" or bumpState == "BUMPED RIGHT" or bumpState == "BUMPED LEFT AND RIGHT": 
					#rotate
					variance = decimal.Decimal(random.randrange(-35,35))/100 
					variance = float(variance)
					
					if bumpState == "BUMPED LEFT":
						print("Rotating Left")
						lock.acquire()
						_robot.driveStraight(_DRIVE_ROTATE_REVERSE, _DRIVE_ROTATE_FORWARD)
						time.sleep(_ROTATE_TIME + variance)#turn for 180 degrees
						lock.release()
						#running = True


					elif bumpState == "BUMPED RIGHT":
						print("Rotating Right")
						lock.acquire()
						_robot.driveStraight(_DRIVE_ROTATE_FORWARD,_DRIVE_ROTATE_REVERSE)
						time.sleep(_ROTATE_TIME + variance)#turn for 180 degrees
						lock.release()
									
					elif bumpState == "BUMPED LEFT AND RIGHT":
						#randomly chooses a direction to turn
						turn = bool(random.getrandbits(1))
						print("Turning Random")
						if turn:
							lock.acquire()
							_robot.driveStraight(_DRIVE_ROTATE_REVERSE,_DRIVE_ROTATE_FORWARD)
							time.sleep(_ROTATE_TIME + variance)
							lock.release()
							#running = True
						
						else:
							lock.acquire()
							_robot.driveStraight(_DRIVE_ROTATE_FORWARD,_DRIVE_ROTATE_REVERSE)
							time.sleep(_ROTATE_TIME + variance)
							lock.release()
							#turn for 180 degrees
							#running = True
				
				
'''
This method is constantly checking to see if the cliff sensors of the 
robot are activated. The robot takes action based on any cliff sensor
being activated. 
'''
def ListenCliffs():
	global driving, cliffActivated, running
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



'''
This method listens to see if the CLEAN button has been pressed on the robot.
If so it changes stopDriving to true, which should alert the driver() method to 
stop driving
'''
def ListenButtons(): 
	global listening, running, driving #isCliffDetected #given access to stopDriving
	#previous = 0
	while listening: #the robot is listening for button clicks
			lock.acquire()
			a = _robot.readButton(jaguar.Buttons['_CLEAN']) #boolean for if the button has been clicked 
			lock.release()
			if a:
				driving = not driving
				#running = not running
				#print("CLEAN BUTTON TOGGLED." + "  " + str(driving))
			time.sleep(0.5)



_robot = jaguar.Jaguar() #initilizes robot by setting it in passive and safe mode
time.sleep(.01) #process time

_robot.changeState(jaguar.States['_FULL'])

t1 = threading.Thread(target = Drive) #first thread for listening
t2 = threading.Thread(target = ListenCliffs) #second thread for driving
t3 = threading.Thread(target = ListenBumps)
t4 = threading.Thread(target = ListenButtons)


print("START")
t2.start() #starts the second thread
t3.start()
t4.start()
t1.start() #start the first thread

