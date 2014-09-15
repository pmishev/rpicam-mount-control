#!/usr/bin/env python
#-----------------------------------
# Name: RpiCam Stand Control
#
# Author: Plamen Mishev
# Created: 10/09/2014
#-----------------------------------

# TODO: Make fifo file on-the-fly

#import threading
import thread
import os
#import fcntl
import time
import sys
import errno
import RPi.GPIO as GPIO
import keyhandler

# Use physical pin numbers
GPIO.setmode(GPIO.BOARD)
 
FIFO = "commands.fifo" 	# The FIFO file where we read commands from
waitTime = 0.001 		# Seconds to wait after each iteration

char = None 			# The currently pressed keyboard key
command = ''			# The command received from the queue

class MotorControl:

	STOPPED = 0
	MOVING_LEFT = 1
	MOVING_RIGHT = 2

	# Set the manufacturer defined sequence of pin states in order to move the motor
	SEQUENCE = [[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]

	# motorAlias: The name that motor will be called
	# pins: list of the 4 pins controlling the motor
	def __init__(self, motorAlias, pins):

		self.motorAlias = motorAlias
		self.pins = pins
		self.state = MotorControl.STOPPED
		self.stepCounter = 0

		# Set all motor pins as output
		print "Setting up pins of motor %s" %(self.motorAlias)
		for pin in self.pins:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, False)


	# Rotate the motor a single step, if it's supposed to be moving
	def updateMotor(self):

		if (self.state == MotorControl.STOPPED):
			return

		if (self.state == MotorControl.MOVING_LEFT):
			if self.stepCounter <= 0:
				self.stepCounter = 7
			else:
				self.stepCounter -= 1

		elif (self.state == MotorControl.MOVING_RIGHT):
			if self.stepCounter >= 7:
				self.stepCounter = 0
			else:
				self.stepCounter += 1

		# Go through each of the 4 controlling pins
		for pin in range(0, 4):
			pinNumber = self.pins[pin]
			# Depending on the manufacturer defined sequence, switch the pin on or off
			if MotorControl.SEQUENCE[self.stepCounter][pin] != 0:
				#print " Step %i Enable %i" %(self.stepCounter,pinNumber)
				GPIO.output(pinNumber, True)
			else:
				GPIO.output(pinNumber, False)
			

	def setState(self, state):
		self.state = state

def getCommand():
	# Check if there is a command waiting in the queue
	try:
		fifo = os.open(FIFO, os.O_RDONLY | os.O_NONBLOCK)
		command = os.read(fifo, 30).strip()
		os.close(fifo)
	except OSError, e:
		# If the fifo file is currently open for writing, one of these exceptions would happen
		if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
			#print "Error({0}): {1}".format(e.errno, e.strerror)
			command = ''

	return command


# Function that waits until a key is pressed and sets the key in the global scope
def keypressDetector():
	global char
	while True:
		if type(keyhandler).__name__ == 'module':
			char = keyhandler.getKey()
		if type(time).__name__ == 'module':
			time.sleep(0.005) # Bad things happen for some reason if there's no sleep at all

try:
	# Initialize motors
	horizontalMotor = MotorControl('horizontal', [16,12,10,8])
	verticalMotor   = MotorControl('vertical',   [19,15,13,11])
	motors = [horizontalMotor, verticalMotor]

	# Start the keypress detector in a separate thread, so it doesn't block the main program execution
	thread.start_new_thread(keypressDetector, ())


	# Start the main loop
	while True:

		command = getCommand()		

		if command != '':
			print command

		if char is not None:
			#print "Key pressed is: {}".format(char)
			if char == 'q':
				sys.exit()
			elif char == 'a':
				print "Go left"
				horizontalMotor.setState(MotorControl.MOVING_LEFT)
			elif char == 'd':
				print "Go right"
				horizontalMotor.setState(MotorControl.MOVING_RIGHT)
			elif char == 'w':
				print "Go up"
				verticalMotor.setState(MotorControl.MOVING_LEFT)
			elif char == 's':
				print "Go down"
				verticalMotor.setState(MotorControl.MOVING_RIGHT)
			elif char == 'r':
				print "Stop horizontal"
				horizontalMotor.setState(MotorControl.STOPPED)
			elif char == 'f':
				print "Stop vertical"
				verticalMotor.setState(MotorControl.STOPPED)

			char = None

		for motor in motors:
			motor.updateMotor()

		time.sleep(waitTime)

# Stop on Ctrl+C and clean up
except (KeyboardInterrupt, SystemExit):
	print "Exiting"
	GPIO.cleanup()

