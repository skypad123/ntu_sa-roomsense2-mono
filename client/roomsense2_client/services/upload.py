
import requests 
from datetime import datetime
import os 
import json
import logging
import sys
from dotenv import load_dotenv
from getmac import get_mac_address as gma # mac address
from typing import Optional, Callable
from dataclasses import dataclass
import threading
import asyncio

## <-- component types for device information -->
@dataclass
class DeviceMeta:
    device: str
    userSetLocation: Optional[str] = None
    sensors: Optional[list[str]] = None
    
    def to_dict(self):
        ret = {
            "device": self.device,
            "userSetLocation": self.userSetLocation
        }
        if self.sensors is not None:
            ret["sensors"] = self.sensors
        return ret


async def insert_device(backend_url: str): 
    url = backend_url + "/update/device"

    headers = {
        'Content-Type': 'application/json'
    }

    device_name = os.getenv("DEVICE_NAME")
    if device_name is None:
        raise Exception("DEVICE_NAME not set")
    user_set_location = os.getenv("USER_SET_LOCATION")
    sensors = os.getenv("SENSORS_LIST")
    if sensors is not None:
        sensors = sensors.split(",")
    payload = DeviceMeta(device=device_name, userSetLocation=user_set_location, sensors=sensors).to_dict()

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    
    logging.debug(response.text)
    return response.json()
## <-- component types for device information -->

## <-- component types for timeseries log data -->
@dataclass
class HumidityTemperature:
    humidity: float
    temperature: float

    def to_dict(self):
        return {
            "humidity": self.humidity,
            "temperature": self.temperature
        }
    
@dataclass
class Co2HumidityTemperature:
    co2: float
    humidity: float
    temperature: float

    def to_dict(self):
        return {
            "co2": self.co2,
            "humidity": self.humidity,
            "temperature": self.temperature
        }
    
@dataclass
class Brightness:
    brightness: float

    def to_dict(self):
        return {
            "brightness": self.brightness
        }

@dataclass   
class IRImage:
    frame: list[float]

    def to_dict(self):
        return {
            "frame": self.frame
        }

    
@dataclass 
class Image:
    imageUrl: str

    def to_dict(self):
        return {
            "imageUrl": self.imageUrl
        }
    
@dataclass
class Audio:
    audioUrl: str

    def to_dict(self):
        return {
            "audioUrl": self.audioUrl
        }

@dataclass
class Metadata:
    device: str
    sensor: str
    
    def to_dict(self):
        return {
            "device": self.device,
            "sensor": self.sensor
        }

#shorthand for OR operator typing on "data" field
HT = HumidityTemperature
B = Brightness
CHT = Co2HumidityTemperature
I = Image
A = Audio
IR = IRImage

@dataclass
class TimeseriesLog: 
    timestamp: datetime
    metadata: Metadata
    objectId: Optional[str] = None
    data: Optional[HT|B|CHT|I|A|IR] = None

    def to_dict (self):        
        ret = {
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata.to_dict(),
            "data": self.data.to_dict()
        }
        if self.objectId is not None:
            ret["objectId"] = self.objectId
        return ret
    
async def insert_timeseries(backend_url: str, timestamp: datetime, device_name: str, sensor: str , data: HT|B|CHT|I|A): 
    url = backend_url + "/update/log"

    metadata = Metadata(device=device_name, sensor=sensor)
    payload = TimeseriesLog(timestamp=timestamp, metadata=metadata, data=data).to_dict()

    headers = {
        'Content-Type': 'application/json'
    }
    
    res = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    logging.debug(res.text)
    return res.json()

async def register_device(base_url:str,device_location: Optional[str] ,sensors: Optional[list[str]]):
    json_data = {
        "device": gma(),
        "userSetLocation": device_location,
    }
    if sensors is not None:
        json_data["sensors"] = sensors
    res = requests.post( f"{base_url}/update/device", json=json_data)

    logging.debug(res.text)
    return res.json()


async def upload_image(base_url:str):
    url = f"{base_url}/upload/image"
    file = open('temp/image.jpg', 'rb')
    files = {'file': ('image.jpg', file, 'image/jpeg')}

    res = requests.post(url, files=files, timeout=30)
    file.close()
    return res.json()


async def upload_audio(base_url:str):
    url = f"{base_url}/upload/audio"
    file = open('temp/audio.wav', 'rb')
    files = {'file': ('audio.wav', file, 'audio/wav')}

    res = requests.post(url, files=files, timeout=30)
    file.close()
    return res.json()


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)    

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    load_dotenv()
    backend_url = os.getenv("API_ENDPOINT")

    p = threading.Thread(target=asyncio.run, \
                        args=((insert_timeseries(backend_url, datetime.now(), "prototype #1", "SCD41", CHT(co2=100, humidity=50, temperature=25)),)))
    # upload_image(backend_url)
    # insert_timeseries(backend_url, datetime.now(), "prototype #1", "SCD41", CHT(co2=100, humidity=50, temperature=25))
    p.start()
    p.join()


