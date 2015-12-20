# ChristmasPi-LightShow
Simple christmas light controller and pattern generator for raspberry pi

Currently only 8 lights, since that's all I need this Christmas.

* Generate a pattern of appropriate length with GeneratePattern.py
* Modify it to turn lights on (1) or off (0) in the appropriate positions
* Test using the built-in simulator
* Deploy to your RPi

eg: ./GeneratePattern.py --bpm 136.88 --duration 227.45 --start 1.25 > LetItGo.pattern
    (Edit LetItGo.pattern)
    ./LightPlayer.py --music LetItGo.mp3 --pattern LetItGo.pattern

    (Adjust GPIO pins in LightPlayer.py according to your setup)
    ./LightPlayer.py --music LetItGo.mp3 --pattern LetItGo.pattern --live
