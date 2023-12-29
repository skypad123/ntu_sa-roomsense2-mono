from time import sleep
from picamera import PiCamera

# import os

# os.chmod( "../temp", 755)

camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture('../temp/image.jpg')