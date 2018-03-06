#!/user/bin/env python

import linguist
import jaguar

import serial
import struct 
import time
import threading

stop = False #boolean for robot is stopped
running = False #boolean for robot is running
listen = True #robot is listening
stopDriving = False
lock = threading.Lock() #"Once a thread has acquired a lock, subsequent attempts to acquire it block, until it is released; any thread may release it.


_DRIVE_STRAIGHT_SPEED = 150
_DRIVE_STRAIGHT_RADIUS = 0
_DRIVE_STRAIGHT_TIME = 1

_ROTATE_SPEED = 41
_ROTATE_RADIUS = 1
_ROTATE_TIME = .05

_STOP_DRIVING_SPEED = 0
_STOP_DRIVING_RADIUS = 0 

'''
This method is going to have the robot drive around in a pentagon
'''
def driver():
	global stopDriving #access given to the stopDriving variable
	running = True
	turns= 5 #number of turns needed
	while turns>0:  #while there are still turns to be made
		if stop:
			break
		time.sleep(1) #time to process 

		lock.acquire()
		_robot.drive(_DRIVE_STRAIGHT_SPEED,_DRIVE_STRAIGHT_RADIUS) #drive straight 
		lock.release()
		time.sleep(_DRIVE_STRAIGHT_TIME) #drives straight for 1.8 seconds
		
		if stopDriving or turns == 1: #if stopDriving is true, then jump out of the while loop before the robot rotates
			print("ROBOT STOPPED")
			break
			
		lock.acquire()
		_robot.drive(_ROTATE_SPEED,_ROTATE_RADIUS) #Rotate
		lock.release()
		time.sleep(_ROTATE_TIME) #rotate for .8 seconds
		turns-=1

	lock.acquire()
	_robot.drive(_STOP_DRIVING_SPEED,_STOP_DRIVING_RADIUS)
	lock.release()
	if turns == 0:
		print("PENTAGON DRAWN")
	stopDriving = True 
	listen = True #stop listening 
	raise SystemExit

'''
This method listens to see if the CLEAN button has been pressed on the robot.
If so it changes stopDriving to true, which should alert the driver() method to 
stop driving
'''
def listen(): 
	global stopDriving #given access to stopDriving
	while listen: #the robot is listening for button clicks 
		lock.acquire()
		a = _robot.readButton(jaguar.Buttons['_CLEAN']) #boolean for if the button has been clicked 
		lock.release()
		
		if a: #means button is clicked
			if running: #if the robot is driving
				stopDriving = True
				print("CLEAN BUTTON TOGGLED. STOPPING THE ROBOT")
				#_robot.drive(0,0)
				break

'''
Method to draw the pentagon. Uses threading to have listen() and driver() running at once
'''
#def pentagon():
_robot = jaguar.Jaguar() #initilizes robot by setting it in passive and safe mode
time.sleep(1) #process time

#this while loop keeps the method from moving forward until the clean button has been clicked
while not running: #while the robot is idle
	if _robot.readButton(jaguar.Buttons['_CLEAN']): #if the clean button is clicked,
		running = True #running is set to true
		break #the while loop is broken out 
	time.sleep(.05)
time.sleep(.5) #process time
_robot.changeState(jaguar.States['_FULL'])
print("BEGINNING TO DRAW PENTAGON")
t1 = threading.Thread(target = listen) #first thread for listening
t2 = threading.Thread(target = driver) #second thread for driving
t1.start() #start the first thread
t2.start() #starts the second thread

#pentagon() #kicks everything off


