#!/usr/bin/env python

import threading
import time
import sys
import RPi.GPIO as GPIO
import keyhandler

waitTime = 0.001


char = None;

# Function that waits until a key is pressed and sets the key in the global scope
def keypressDetector():
	global char
	while True:
		#try:
			char = keyhandler.getKey()
			time.sleep(0.005) # Bad things happen for some reason if there's no sleep at all
		#except:
			# Sometimes after the main program terminates, the keyhandler object is destroyed before this thread has finished
			# We catch the exception to avoid outputting ugly error message in that case
		#	pass



try:
	# Start the keypress detector in a separate thread, so it doesn't block the main program execution
	#thread.start_new_thread(keypressDetector, ())
	keyHandlerThread = threading.Thread(target=keypressDetector, name="keyHandler")
	keyHandlerThread.start()

	# Start the main loop
	while True:
		if char is not None:
			#print "Key pressed is: {}".format(char)
			if char == 'q':
				sys.exit()
			elif char == 'a':
				print "Go left"
			elif char == 'd':
				print "Go right"
			elif char == 'w':
				print "Go up"
			elif char == 's':
				print "Go down"

			char = None

		time.sleep(waitTime)

# Stop on Ctrl+C and clean up
except (KeyboardInterrupt, SystemExit):
	print "Exiting"
	#GPIO.cleanup()

