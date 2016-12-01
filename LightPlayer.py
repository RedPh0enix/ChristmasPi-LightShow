#!/usr/bin/python
#
# Christmas Light pattern player for Raspberry Pi
#
# Todo: Switch to cvlc with --start-time=x (seconds) for testing/skipping.

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
parser.add_argument('-t','--test', action='store_true', help='test metronome for bps sync')
parser.add_argument('-f','--faces', action='store_true', help='Treat the last 8 lights as face components')
parser.add_argument('-F','--bigfaces', action='store_true', help='Use big ascii faces')
parser.add_argument('-v','--verify', action='store_true', help="Verify face part accuracy")
parser.add_argument('-s','--skip', help='seconds to skip before playing')
args=parser.parse_args()

LIVE=False
if(args.live):
	# Performance mode active
	print "Performance mode active"
	LIVE=True

FACES=False
if(args.faces):
	FACES=True

BIGFACES=False
if(args.bigfaces):
	BIGFACES=True


METRONOME=False
if(args.test):
	# Test metronome
	print "Metronome mode active"
	METRONOME=True

if(LIVE):
	import RPi.GPIO as GPIO

# These are the GPIO pins associated with each light.
# Change this for your setup.
#pinList = [4, 17, 27, 22, 5, 6, 13, 19]
pinList = [4, 17, 27, 22, 5, 6, 13, 19, 18, 23, 24, 25, 12, 16, 20, 21]

musicPath=""
patternPath=""
skipSeconds=0

if(args.music):
	musicPath = args.music

if(args.pattern):
	patternPath = args.pattern

if(args.skip):
	skipSeconds = int(args.skip)

# Check our files
if(os.path.isfile(musicPath) == False and args.verify != True):
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
if(skipSeconds):
	startTime = startTime - (skipSeconds * 1000)

if(args.music != ""):
	if(args.skip):
		subprocess.Popen(['cvlc', '--start-time='+str(skipSeconds), musicPath])
	else:
		subprocess.Popen(['mpg123', '-q', musicPath])

# Keep light state, for demo mode
lightStatus=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


ticker = 0
for line in pattern:
	if(re.search("^#",line)):
		# Ignore this line completely.
		continue
	
	elements = line.split("\t")

	# Is there anything at all to do in this line?
	flashes = ''.join(map(str,elements[1:]))

	# Has the user requested that we turn lights on or off?
	activity = re.search("[01]",flashes)
	noActivity=True
	if(activity):
		noActivity=False
	

	if(METRONOME):
		# Metronome ticker.
		ticker = ticker + 1
		if(ticker > 3):
			ticker = 0

		noActivity = False
	
	# Nothing to do here. Move along.
	if(noActivity):
		continue

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
			if(args.verify != True or (skipSeconds > 0 and (msec < (skipSeconds *1000)))):
				time.sleep(waitTimeSeconds);

	# Remove the first element from our list now that we have finished with it.
	del elements[0]

	# Ok, execute our pattern
	for idx,action in enumerate(elements):
		# More instructions than pins? Break out.
		if(idx >= len(pinList)):
			break

		pin=pinList[idx]
		action=action[0]

		if(METRONOME):
			if(ticker == 0):
				action = "1"
			else:
				action = "0"

		if(action == "0"):
			lightStatus[idx]=action;
			if(LIVE):
        			GPIO.output(pin, GPIO.HIGH)
		elif(action == "1"):
			lightStatus[idx]=action;
			if(LIVE):
        			GPIO.output(pin, GPIO.LOW)
		
	if(LIVE == False):
		if(args.verify):
			if(lightStatus[9] == "1" and lightStatus[10] == "1" and lightStatus[11] == "1"):
				print "VERIFICATION ERROR: Top mid and bottom mouth are on at [%dm %06.3fs]: " % (minutes,seconds)
				print ""
			if(lightStatus[9] == "0" and lightStatus[11] == "1"):
				print "VERIFICATION ERROR: bottom mouth is on, without top at [%dm %06.3fs]: " % (minutes,seconds)
				print ""
			if(lightStatus[12] == "1" and (lightStatus[9] == "1" or lightStatus[10] == "1" or lightStatus[11]=="1")):
				print "VERIFICATION ERROR: OOOh is on, but top, mid, or bottom are also on at [%dm %06.3fs]: " % (minutes,seconds)
				print ""
			if(lightStatus[14] == "1" and lightStatus[15] == "1"):
				print "VERIFICATION ERROR: Open and closed on face 2 are both on at [%dm %06.3fs]: " % (minutes,seconds)
				print ""
			if(lightStatus[8] == "1" and (lightStatus[9] != "1" and lightStatus[10] != "1" and lightStatus[11] != "1" and lightStatus[12] != "1")):
				print "WARNING: Open eyes, but no mouth at [%dm %06.3fs]: " % (minutes,seconds)
				print ""


		print "Light Status [%dm %06.3fs]: " % (minutes,seconds),
		for idx,light in enumerate(lightStatus):
			if(light == "0"):
				print "---  ",
			else:
				print "*O*  ",

		if(FACES == True):
			# Cheat a bit with our faces.

			faces = ''
			if(lightStatus[8] == "1"):
				faces=faces+'8'
			else:
				faces=faces+' '
			
			if(lightStatus[12] == "1"):
				faces=faces+'( )'
			else:
				if(lightStatus[9] == "1" and lightStatus[10] == "1"):
					faces=faces+'[] '
				elif(lightStatus[9] == "1" and lightStatus[11] == "1"):
					faces=faces+'[ ]'
				elif(lightStatus[10] == "1"):
					faces=faces+' } '
				else:
					faces=faces+'   '


			faces=faces + '    '

			for i in range(0,3):
				if(lightStatus[13] == "1"):
					faces=faces+'8'
				else:
					faces=faces+' '
	
				if(lightStatus[14] == "1"):
					faces=faces+'[] '
				elif(lightStatus[15] == "1"):
					faces=faces+'[ ]'
				else:
					faces=faces+'   '

				faces = faces + '   '

			print faces,

		if(BIGFACES == True):
			print ""
			faces1=""
			faces2=""
			faces3=""
			faces4=""
			faces5=""
			faces6=""
			faces7=""
			faces8=""

			if(lightStatus[8] == "1"):
				faces1="          |\     /|        "
				faces2="          | \   / |        "
				faces3="          |__\ /__|        "
			else:
				faces1="                           "
				faces2="                           "
				faces3="                           "
			
			if(lightStatus[9] == "1" and lightStatus[10] == "1"):
				faces4="                           "
				faces5="          |\_____/|        "
				faces6="          |       |        "
				faces7="           \_____/         "
				faces8="                           "
			elif(lightStatus[9] == "1" and lightStatus[11] == "1"):
				faces4="                           "
				faces5="          |\_____/|        "
				faces6="          |       |        "
				faces7="          |       |        "
				faces8="           \_____/         "
			elif(lightStatus[9] == "0" and lightStatus[10] == "1"):
				faces4="                           "
				faces5="                           "
				faces6="          |       |        "
				faces7="           \_____/         "
				faces8="                           "
			elif(lightStatus[12] == "1"):
				faces4="            _____          "
				faces5="           /     \         "
				faces6="          |       |        "
				faces7="          |       |        "
				faces8="           \_____/         "
			else:
				faces4="                           "
				faces5="                           "
				faces6="                           "
				faces7="                           "
				faces8="                           "
			
			if(lightStatus[13] == "1"):
				faces1 = faces1 + "|\     /|  |\     /|  |\     /|   "
				faces2 = faces2 + "| \   / |  | \   / |  | \   / |   "
				faces3 = faces3 + "|__\ /__|  |__\ /__|  |__\ /__|   "

			if(lightStatus[14] == "1"):
				faces4 = faces4 + "                                    "
				faces5 = faces5 + "|\_____/|  |\_____/|  |\_____/|     "
				faces6 = faces6 + "|       |  |       |  |       |     "
				faces7 = faces7 + " \_____/    \_____/    \_____/      "
				faces8 = faces8 + "                                    "
			elif(lightStatus[15] == "1"):
				faces4 = faces4 + "                                    "
				faces5 = faces5 + "|\_____/|  |\_____/|  |\_____/|     "
				faces6 = faces6 + "|       |  |       |  |       |     "
				faces7 = faces7 + "|       |  |       |  |       |     "
				faces8 = faces8 + " \_____/    \_____/    \_____/      "

			print faces1
			print faces2
			print faces3
			print faces4
			print faces5
			print faces6
			print faces7
			print faces8
		else:
			print "             \r",

		sys.stdout.flush()

if(LIVE):
	GPIO.cleanup()

exit()
