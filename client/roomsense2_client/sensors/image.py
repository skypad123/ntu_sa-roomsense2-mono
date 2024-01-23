from picamera import PiCamera

class RpiCamera:
    
    def __init__(self, file_location = "temp/image.jpg"):
        self.file_location = file_location
        self.camera = PiCamera()
        self.camera.resolution = (1024, 768)
        
    def capture(self):
        self.camera.capture(self.file_location)

        