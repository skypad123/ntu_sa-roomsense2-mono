import requests
from typing import Optional
from datetime import datetime
from datetime import timezone

from getmac import get_mac_address as gma # mac address

def register_device(base_url:str,device_location: Optional[str] ,sensors: Optional[list[str]]):
    
    json_data = {
        "device": gma(),
        "userSetLocation": device_location,
    }
    if sensors is not None:
        json_data["sensors"] = sensors
    res = requests.post( f"{base_url}/update/device", json=json_data)
    print(res.json())

class Metadata:
    device: str
    sensor: str

    def __init__(self, device: str, sensor: str):
        self.device = device
        self.sensor = sensor

    def to_dict(self):
        return {
            "device": self.device,
            "sensor": self.sensor,
        }

def send_logs(base_url:str, timestamp: Optional[datetime], metadata: Metadata , data: dict):
    
    if timestamp is None:
        timestamp = datetime.now()

    json_data = {
        "timestamp": timestamp.isoformat(),
        "metadata": metadata.to_dict(),
        "data": data
    }
    res = requests.post( f"{base_url}/update/log", json=json_data)
    print(res.json())

def upload_image():
    pass

def upload_audio():
    pass


if __name__ == "__main__":
    # base_url = "http://localhost:8000"
    # # register_device(base_url, None,["temperature", "humidity"])
    # metadata = Metadata(gma(), "SDC40")
    # data = {
    #     "temperature": 30,
    #     "humidity": 50
    # }
    # send_logs(base_url, datetime.now(), metadata, data)

    pass
