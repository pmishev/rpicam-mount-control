#!/usr/bin/env python
#-----------------------------------
# Name: RpiCam Stand Control
#
# Author: Plamen Mishev
# Created: 10/09/2014
#-----------------------------------

import time
import sys
import errno
import keyhandler

FIFO = "commands.fifo" 	# The FIFO file where the motor controller reads commands from

def sendCommand(command):
	global FIFO
	queue = open(FIFO, 'w')
	queue.write(command)
	queue.close()

try:
	# Start main loop
	while True:

		char = keyhandler.getKey()

		if char == 'q':
			sendCommand('stop')
			sys.exit()
		elif char == 'a':
			print "Go left"
			sendCommand('go left')
		elif char == 'd':
			print "Go right"
			sendCommand('go right')
		elif char == 'w':
			print "Go up"
			sendCommand('go up')
		elif char == 's':
			print "Go down"
			sendCommand('go down')
		elif char == 'r':
			print "Stop horizontal"
			sendCommand('stop horizontal')
		elif char == 'f':
			print "Stop vertical"
			sendCommand('stop vertical')

		# Wait before moving on
		time.sleep(0.001)


# Stop on Ctrl+C and clean up
except (KeyboardInterrupt, SystemExit):
	print "Exiting"
