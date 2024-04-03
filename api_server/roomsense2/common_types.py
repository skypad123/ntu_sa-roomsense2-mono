import datetime
from pydantic import BaseModel
from typing import Optional


class HumidityTemperature(BaseModel):
    humidity: float
    temperature: float

    def to_dict(self):
        return {
            "humidity": self.humidity,
            "temperature": self.temperature
        }

class Co2HumidityTemperature(BaseModel):
    co2: float
    humidity: float
    temperature: float

    def to_dict(self):
        return {
            "co2": self.co2,
            "humidity": self.humidity,
            "temperature": self.temperature
        }

class Brightness(BaseModel):
    brightness: float

    def to_dict(self):
        return {
            "brightness": self.brightness
        }
    
class IRImage(BaseModel):
    frame: list[float]

    def to_dict(self):
        return {
            "frame": self.frame
        }

    
class Image(BaseModel):
    imageUrl: str

    def to_dict(self):
        return {
            "imageUrl": self.imageUrl
        }

class Audio(BaseModel):
    audioUrl: str

    def to_dict(self):
        return {
            "audioUrl": self.audioUrl
        }
    
class ImageProcessed(BaseModel):
    imageUrl: str

    def to_dict(self):
        return {
            "imageUrl": self.imageUrl,
        }

class AudioProcessed(BaseModel):    
    audioUrl: str

    def to_dict(self):
        return {
            "audioUrl": self.audioUrl,
        }
    

class Metadata(BaseModel):
    device: str
    sensor: str
    
    def to_dict(self):
        return {
            "device": self.device,
            "sensor": self.sensor
        }

DHT11Data = HumidityTemperature
TSL2591Data = Brightness
S8Data = Co2HumidityTemperature
HTU2XData = HumidityTemperature
SCD30Data = Co2HumidityTemperature
SCD40Data = Co2HumidityTemperature
ImageData = Image
AudioData = Audio
MLX90640Data = IRImage

#shorthand for OR operator typing on "data" field
HT = HumidityTemperature
B = Brightness
CHT = Co2HumidityTemperature
I = Image
A = Audio
IR = IRImage

class TimeseriesLog(BaseModel): 
    timestamp: datetime.datetime
    metadata: Metadata
    objectId: Optional[str] = None
    data: Optional[B|CHT|HT|I|A|IR] = None

    def to_dict (self):        
        ret = {
            "timestamp": self.timestamp,
            "metadata": self.metadata.to_dict(),
            "data": self.data.to_dict()
        }
        if self.objectId is not None:
            ret["objectId"] = self.objectId
        return ret
    
        

class DeviceMeta(BaseModel):
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

