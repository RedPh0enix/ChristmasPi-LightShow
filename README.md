# ChristmasPi-LightShow
Simple christmas light controller and pattern generator for raspberry pi

Updated to cope with 16 lights.

The first 8 lights are assumed to be normal blinkers.
The next 5 lights make up a face
* Light 9 represents eyes
* Light 10 is a 'Smile'
* Light 11 is a wide open mouth
* Light 12 is a partially open mouth
* Light 13 is a mouth in a "O" pattern.

The next 3 represent a third less complex face
* Light 14 represents eyes
* Light 15 is a wide open mouth
* Light 16 is a partially open mouth

* Generate a pattern of appropriate length with GeneratePattern.py
* Modify it to turn lights on (1) or off (0) in the appropriate positions
* Test using the built-in simulator
* Deploy to your RPi


eg: ./GeneratePattern.py --bpm 136.88 --duration 227.45 --start 1.25 > LetItGo.pattern
    (Edit LetItGo.pattern, based on time signatures for interesting events in Audacity)
    ./LightPlayer.py --music LetItGo.mp3 --pattern LetItGo.pattern

    (Adjust GPIO pins in LightPlayer.py according to your setup)
    ./LightPlayer.py --music LetItGo.mp3 --pattern LetItGo.pattern --live

To determine BPM figures, I use audacity, and generate a click track. Keep adjusting the BPM figures until it matches the associated MP3.
