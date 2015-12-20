#!/usr/bin/python
#
# Christmas Light pattern player for Raspberry Pi
#

import time
import re
import os
import subprocess
import signal
import sys
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-l','--live', action='store_true', help='Turn on live performance mode')
parser.add_argument('-m','--music', help='mp3 to play')
parser.add_argument('-p','--pattern', help='pattern to play')
args=parser.parse_args()

LIVE=False
if(args.live):
	# Performance mode active
	print "Performance mode active"
	LIVE=True

if(LIVE):
	import RPi.GPIO as GPIO

# These are the GPIO pins associated with each light.
# Change this for your setup.
pinList = [4, 17, 27, 22, 5, 6, 13, 19]

musicPath=""
patternPath=""

if(args.music):
	musicPath = args.music

if(args.pattern):
	patternPath = args.pattern

# Check our files
if(os.path.isfile(musicPath) == False):
	print "Cannot find music file ",musicPath
	sys.exit(1)
if(os.path.isfile(patternPath) == False):
	print "Cannot find pattern file ",patternPath
	sys.exit(1)

# Ok.. all set up, ready to go.

if(LIVE):
	GPIO.setmode(GPIO.BCM)

def signal_handler(signal,frame):
	print "\n\nShutting down"
	if(LIVE):
		GPIO.cleanup()
	sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)

# loop through pins and set mode and state to 'low'
if(LIVE):
	for i in pinList: 
	    GPIO.setup(i, GPIO.OUT) 
	    GPIO.output(i, GPIO.HIGH)

# Load up our pattern file
patternFile = open(patternPath,"r")
pattern = patternFile.readlines()

startTime = time.time() * 1000
subprocess.Popen(['mpg123', '-q', musicPath])

# Keep light state, for demo mode
lightStatus=[0,0,0,0,0,0,0,0]

for line in pattern:
	# Is there anything at all to do in this line?
	noActivity = re.search("^[^\t][\t\-]{16}",line)
	
	# Nothing to do here. Move along.
	if(noActivity):
		continue

	elements = line.split("\t")
	patternTime=elements[0]
	timeSearch = re.search("^([0-9]+)m ([0-9\.]+)s",patternTime)

	now=time.time() * 1000
	if(timeSearch):
		minutes=timeSearch.group(1)
		minutes=int(minutes)
		seconds=timeSearch.group(2)
		seconds=float(seconds)
		msec = ((minutes * 60) + seconds)*1000
		waitTime=(startTime + msec) - now
		# Convert waittime to seconds
		if(waitTime > 0):
			waitTimeSeconds=waitTime / 1000;
			#print "Seconds to wait: ",waitTimeSeconds;
			time.sleep(waitTimeSeconds);
		
	# Ok, execute our pattern
	for idx,action in enumerate(elements[1:9]):
		pin=pinList[idx]
		action=action[0]
		if(action == "0"):
			lightStatus[idx]=action;
			if(LIVE):
        			GPIO.output(pin, GPIO.HIGH)
		elif(action == "1"):
			lightStatus[idx]=action;
			if(LIVE):
        			GPIO.output(pin, GPIO.LOW)
		
	if(LIVE == False):
		print "Light Status [%dm %06.3fs]: " % (minutes,seconds),
		for idx,light in enumerate(lightStatus):
			if(light == "0"):
				print "---  ",
			else:
				print "*O*  ",
		print "\r",
		sys.stdout.flush()

if(LIVE):
	GPIO.cleanup()

exit()
