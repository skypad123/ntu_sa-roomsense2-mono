import board
# from adafruit_bh1750 import BH1750
from adafruit_mlx90640 import MLX90640
from dataclasses import dataclass
import asyncio
import datetime

# @dataclass
# class BH1750Reading:
#     lux_reading : float

@dataclass
class MLX90640Reading:
    frame : list[float]


async def read_mlx90640(i2c_bus, timeout = datetime.timedelta(0,1,0)) -> MLX90640Reading:
    sensor = MLX90640(i2c_bus)
    sensor.refresh_rate = MLX90640.RefreshRate.REFRESH_32_HZ

    frame = [0] * 768
    start_time = datetime.datetime.now()
    while True:  
        try:
            sensor.getFrame(frame)
        except ValueError:
            # these happen, no biggie - retry
            if start_time < datetime.datetime.now() - timeout:
                raise TimeoutError("SCD41 did not return data in time") 
            asyncio.sleep(1)
            continue
        return MLX90640Reading(frame=frame)

    return BH1750Reading(lux_reading=sensor.lux)

if __name__ == "__main__":
    i2c = board.I2C()
    asyncio.run(run_mlx90640(i2c))