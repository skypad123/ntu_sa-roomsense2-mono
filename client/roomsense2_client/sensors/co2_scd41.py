from dataclasses import dataclass
import board
from adafruit_scd4x import SCD4X
import datetime
import asyncio

@dataclass
class SCD41Reading:
    co2 : int
    temperature : float
    humidity: float

async def read_scd41(i2c_bus, timeout = datetime.timedelta(0,1,0) ) -> SCD41Reading:
    scd4x = SCD4X(i2c_bus)
    scd4x.measure_single_shot()

    start_time = datetime.datetime.now()

    while True:
        if scd4x.data_ready:
            return SCD41Reading(co2=scd4x.CO2, temperature=scd4x.temperature, humidity=scd4x.relative_humidity)
        else:
            if start_time < datetime.datetime.now() - timeout:
                raise TimeoutError("SCD41 did not return data in time") 
            asyncio.sleep(1)

if __name__ == "__main__":
    i2c = board.I2C()
    asyncio.run(read_scd41(i2c))