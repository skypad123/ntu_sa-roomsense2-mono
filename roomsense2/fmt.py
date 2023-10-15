from datetime import datetime
import tomli
from typing import Optional
from pydantic import BaseModel, Field
from roomsense2.common_types import DeviceMeta, TimeseriesLog

## classes for Multi Retrival Routes
class DeviceMultiRetreivalRequest(BaseModel):
    device: Optional[str] = None
    sensor: Optional[list[str]] = None
    userSetLocation: Optional[str] = None
    cursor: Optional[int] = None
    limit: Optional[int]  = None

class TimeseriesMultiRetreivalRequest(BaseModel): 
    datetime: Optional[datetime] = None
    device: Optional[str] = None
    sensor: Optional[list[str]] = None
    dataFields: Optional[list[str]] = None
    cursor: Optional[int] = None
    limit: Optional[int] = None


#usable for Device & Time Series Retrival Response
class RetreivalResponse:
    apiVersion: str 
    status: str #sucess/interface error/internal server error
    result: Optional[dict | list | None] = None


    def __init__(self) -> None:
        with open('pyproject.toml', 'rb') as toml_file:
            pyproject_data = tomli.load(toml_file)
            self.apiVersion = pyproject_data['tool']['poetry']['version']

    def set_status(self, status:str):
        self.status = status

    def to_dict(self):
        ret = {
            "apiVersion": self.apiVersion,
        }
        if self.status is not None:
            ret["status"] = self.status
        if self.result is not None:
            ret["result"] = self.result
        return ret

## classes for Upload Routes
UploadDeviceRequest = DeviceMeta
UploadLogRequest = TimeseriesLog

class UploadResponse:
    apiVersion: str 
    status: str #sucess/interface error/internal server error
    result: Optional[dict] = None

    def __init__(self):
        with open('pyproject.toml', 'rb') as toml_file:
            pyproject_data = tomli.load(toml_file)
            self.apiVersion = pyproject_data['tool']['poetry']['version']

    def set_status(self, status:str):
        self.status = status

    def to_dict(self):
        ret = {
            "apiVersion": self.apiVersion,
        }

        if self.status is not None:
            ret["status"] = self.status
        if self.result is not None:
            ret["result"] = self.result
        return ret
    
## result field objects
class S3UploadResponse(UploadResponse):
    link: Optional[str] = None 

    def set_status(self, status:str):
        super().set_status(status)

    def to_dict(self):
        if self.link is not None:
            self.result = {
                "link": self.link
            }
        return super().to_dict()

class MongodbUploadResponse(UploadResponse):
    insertedId: Optional[str] = None 

    def set_status(self, status:str):
        self.status = status

    def to_dict(self):
        if self.insertedId is not None: 
            self.result = {
                "insertedId": self.insertedId
            }
        return super().to_dict()
    
