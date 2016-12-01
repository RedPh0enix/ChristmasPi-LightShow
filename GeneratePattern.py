#!/usr/bin/python
#
# Generate BPM figures in audacity by generating a click track, and gradually
# refining against the raw mp3.

import time
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-b','--bpm', help='Beats Per Minute of the source music')
parser.add_argument('-d','--duration', help='total song duration in seconds')
parser.add_argument('-s','--start', help='first song note in seconds')
args=parser.parse_args()

BPM=60.0
Duration=0.0
StartTime=0

if(args.bpm):
	BPM=float(args.bpm)

if(args.duration):
	Duration=float(args.duration)

if(BPM == 0):
	parser.print_help()
	exit()
if(Duration == 0):
	parser.print_help()
	exit()

if(args.start):
	StartTime=float(args.start)

if(StartTime > 0):
	#print "0m 00.000s	0	0	0	0	0	0	0	0"
	print "0m 00.000s	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0"

t=StartTime;
counter=0
while(t <= Duration):
	m=int(t/60.0)
	s=t-(m*60.0)
	print "%dm %06.3fs	-	-	-	-	-	-	-	-" % (m,s),
	# print "%dm %06.3fs	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-" % (m,s),
	if((counter %16)==0):
		print "\t#"
	elif((counter%4)==0):
		print "\t."
	else:
		print
	t=t+(60.0/(BPM*4.0))
	#t=t+(60.0/(BPM))
	counter=counter+1
