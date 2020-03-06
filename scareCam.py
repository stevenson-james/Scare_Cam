import RPi.GPIO as GPIO
from os.path import join as pjoin
import time
import picamera
from time import sleep, gmtime, strftime
from pygame import mixer

filename = "scare_" + strftime("%m-%d %H:%M:%S", gmtime()) + ".h264"
path_to_file = pjoin("Scare Vids", filename)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
#PIR Sensor setup
GPIO.setup(11, GPIO.IN)

camera = picamera.PiCamera()
camera.resolution = (640, 480)

while True:
    #sleep to allow for turning on of scare cam
    #time.sleep(5)
    i=GPIO.input(11)
    if i==0:
        print("No intruders",i)
        time.sleep(1)
    elif i==1:
        print("Intruder detected",i)
        
        mixer.init()
        mixer.music.load("scream.mp3")
        mixer.music.play()

        #save to "path to file"
        camera.start_recording(path_to_file)
        camera.start_preview()
        camera.wait_recording(8)
        camera.stop_recording()
        camera.stop_preview()
        camera.close()
        mixer.music.stop()
        print("video recording stopped")
        break