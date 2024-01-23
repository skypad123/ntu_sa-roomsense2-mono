import board
from adafruit_bh1750 import BH1750
from dataclasses import dataclass
import asyncio


@dataclass
class BH1750Reading:
    lux_reading : float

async def read_bh1750( i2c_bus) -> BH1750Reading:
    sensor = BH1750(i2c_bus)
    return BH1750Reading(lux_reading=sensor.lux)

if __name__ == "__main__":
    i2c = board.I2C()
    asyncio.run(read_bh1750(i2c))