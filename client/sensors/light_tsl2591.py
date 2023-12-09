
from dataclasses import dataclass
import time
import board
from adafruit_tsl2591 import TSL2591
import datetime
import asyncio

@dataclass
class TSL2591Reading:
    lux_reading : float
    infrared : int
    visible : int
    full_spectrum : int

async def read_tsl2591(i2c_bus ) -> TSL2591Reading:
    tsl2591 = TSL2591(i2c_bus)
    print("Total light: {0}lux".format(tsl2591.lux))
    print("Infrared light: {0}".format(tsl2591.infrared))
    print("Visible light: {0}".format(tsl2591.visible))
    print("Full spectrum (IR + visible) light: {0}".format(tsl2591.full_spectrum))
    return TSL2591Reading(lux_reading=tsl2591.lux, infrared=tsl2591.infrared, visible=tsl2591.visible, full_spectrum=tsl2591.full_spectrum)

if __name__ == "__main__":
    i2c = board.I2C()
    asyncio.run(read_tsl2591(i2c))