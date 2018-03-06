CSCE 274
Project 01
Group 5: Khalid Salah, Julian Hong, Logan Fisher

The entire project runs off 3 files:
-linguist.py
-jaguar.py
-pentagon.py

Linguist.py
---------------
-this file imports:
	-serial: for establishing a serial connection
	-time: for allowing pauses between operations

-This file contains the class Linguist, which serves to handle raw communcation between the Raspberry Pi and the iRobot. 

-The class's constuctor calls serialConnection() which sets the serialConnectionM member variable of the class Linguist. 
-The class also handles reading from the serial connection port and closing the serial connection.
-This class also gives the robot the ability to send commands to the serial connectiod by sending in either a list of integers or one integer. These integers represent specific bytes that represent certain actions the robot takes when recieving these bytes

Jaguar.py
--------------
-This file imports and depends on 
	- Linguist: to create a Linguist to handle serial connections
	- serial: debugging
	- struct: to unpack bytes
	- time: to allow pauses between operations

This file contains to dictionaries, Buttons and States, that contain their respective codes. Such as Buttons containg the hex code representing the Clock buttonon the iRobot. And States containg the state code for Full mode.

This file also contains the class Jaguar which represents the being of the robot. The Jaguar contains a Linguist so that it can communicate with the iRobot. The Jaguar is nothing without it's Linguist.

The class Jaguar creates a Linguist on initilization, essentially establishing a serial connection, and then changes it's state to Start and then Passive. 

changeState(self, newState)
The Jaguar can change it's state by recieving the corresponding code for the respective state and then sending that code through a command with the Linguist. The Linguist does all the talking. Cause a Jaguar can't speak English, or code...

readButton(self, button):
The Jaguar can also tell when one of it's buttons has been pushed. The Jaguar asks the Linguist to request sensor data corresponding to the button's on the iRobot. Then the Jaguar's Linguist reads in a byte from the serial port and decides if that byte is the same button as the button that the Jaguar is checking for.

drive(self, velocity, radius):
The Jaguar can also drive when told to do so. It just needs to know what speed to move it's two wheels and what radius to turn in. The Jaguar is a little knowledgeable, so it takes those two integers (velocity and radius), and converts them into high and low bytes for the robot to read because the drive opcode of the iRobot takes in a drive command, a high velocity byte, a low velocity byte, a high radius byte, and a low radius byte. Jaguar packs it all up and has it's Lingusit send the command. 


Pentagon.py
----------------
This file  depends on: 
-Linguist.py
-Jaguar.py
-threading

The purpose of this file is to have the robot draw a pentagon and respond to button clicks. 

This file makes it so the robot can drive and listen for button clicks at the same time.

The driver() function has the robot drive straight 5 times and rotate 108 degrees in space 5 times. If the variable stopDriving is true, the robot stops driving. This variable's variability depends on the function listen(), which changes stopDriving to true when the Clean button has been clicked. 

The listen() function is constantly listening for button clicks and checks if the Clean button has been clicked. When that button has been clicked, the varaiblestopDriving is changed to false, and that is read every time the robot makes a turn. 

The file has a while loop at the end that keeps the robot and everything else from initiating until the clean button has been clicked. Once that has been clicked, the robot begins drawing the polygon, and listens for button clicks to signala stop.




TO RUN THIS PROJECT

scp -r project_01 pi@192.168.1.1:~/ # to transfer files from computer to robot
ssh pi@192.168.1.1 #to set connection with Raspberry Pi

Move into the project_01 directory then,
python pentagon.py  

#this starts the project
 	
