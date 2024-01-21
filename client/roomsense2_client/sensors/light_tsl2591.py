
from dataclasses import dataclass
import board
from adafruit_tsl2591 import TSL2591
import asyncio

@dataclass
class TSL2591Reading:
    lux_reading : float
    infrared : int
    visible : int
    full_spectrum : int

async def read_tsl2591(i2c_bus) -> TSL2591Reading:
    tsl2591 = TSL2591(i2c_bus)
    return TSL2591Reading(lux_reading=tsl2591.lux, infrared=tsl2591.infrared, visible=tsl2591.visible, full_spectrum=tsl2591.full_spectrum)

if __name__ == "__main__":
    i2c = board.I2C()
    asyncio.run(read_tsl2591(i2c))