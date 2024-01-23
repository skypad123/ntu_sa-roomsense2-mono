import board
import digitalio

class HCSRC5031:
    def __init__(self):
        self.pin = board.D4
        self.pir = digitalio.DigitalInOut(self.pin)
        self.pir.direction = digitalio.Direction.INPUT

    def read_motion(self):
        return self.pir.value


if __name__ == "__main__":
    hcsr = HCSRC5031()
    while(1): 
        print(hcsr.read_motion())