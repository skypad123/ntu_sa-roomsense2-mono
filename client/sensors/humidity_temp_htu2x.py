
from dataclasses import dataclass
import board
from adafruit_htu21d import HTU21D
import asyncio

@dataclass
class HTU21DReading:
    temperature : float
    humidity: float

async def read_htu21d(i2c_bus ) -> HTU21DReading:
    htu21d = HTU21D(i2c_bus)
    print("Temperature: %0.1f C" % htu21d.temperature)
    print("Humidity: %0.1f %%" % htu21d.relative_humidity)
    return HTU21DReading(temperature=htu21d.temperature, humidity=htu21d.relative_humidity)

if __name__ == "__main__":
    i2c = board.I2C()
    asyncio.run(read_htu21d(i2c))