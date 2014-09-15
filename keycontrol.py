#!/usr/bin/env python
#-----------------------------------
# Name: RpiCam Stand Control
#
# Author: Plamen Mishev
# Created: 10/09/2014
#-----------------------------------

import thread
import os
import time
import sys
import errno
import keyhandler

FIFO = "commands.fifo" 	# The FIFO file where the motor controller reads commands from
char = None; 			# The currently pressed keyboard key

# Function that waits until a key is pressed and sets the key in the global scope
def keypressDetector():
	global char
	while True:
		# Sometimes on program eit, the thread is still running but the modules are already unloaded, 
		# so we check their existance to avoid error messages
		if type(keyhandler).__name__ == 'module':
			char = keyhandler.getKey()
		if type(time).__name__ == 'module':
			time.sleep(0.005) # Bad things happen for some reason if there's no sleep at all


def sendCommand(command, retries = 5, msgOnError = None):
	global FIFO

	# Make up to X attempts to write to the pipe
	for i in range(retries):

		try:
			queue = os.open(FIFO, os.O_WRONLY | os.O_NONBLOCK)
			try:
				os.write(queue, command)
			except:
				print "writing failed"
			finally:
				os.close(queue)
			# If we managed to write successfully to the pipe, exit from the function
			return

		except OSError, e:
			# If the fifo file is not ready for writing (e.g. a reader is not connected)
			print "opening failed"
			if e.errno == errno.ENXIO:
				sys.stdout.write('.')
				sys.stdout.flush()
				time.sleep(0.5)
				i += 1
			else:
				raise
	if msgOnError == None:
		print "Noone is listening on the other end of the fifo. Aborting command!"
	else:
		print msgOnError	

	return -1

try:
	# Start the keypress detector in a separate thread, so it doesn't block the main program execution
	#thread.start_new_thread(keypressDetector, ())

#	queue = open(FIFO, 'w')
#	queue.write("qwe")
#	queue.close()
#	sys.exit()

#	queue = os.open(FIFO, os.O_WRONLY)
#	try:
#		os.write(queue, "asd")
#	finally:
#		os.close(queue)
#	sys.exit()


	print 'Waiting for motor controller...'
	isListenerReady = sendCommand('', 5, 'Not found!')
	if isListenerReady == -1:
		sys.exit()

	print 'Motor controller ready'

	# Start main loop
	while True:

		if char is not None:
			#print "Key pressed is: {}".format(char)
			if char == 'q':
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

			char = None

		# Wait before moving on
		time.sleep(0.001)


# Stop on Ctrl+C and clean up
except (KeyboardInterrupt, SystemExit):
	print "Exiting"
