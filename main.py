from typing import Union, Annotated

from fastapi import FastAPI, File, UploadFile

from roomsense2.s3 import S3Interface
from roomsense2.fmt import *
from roomsense2.mongodb import *
from roomsense2.errors import *
from dotenv import load_dotenv, dotenv_values


load_dotenv()
config = dotenv_values(".env")

app = FastAPI()
s3_interface = S3Interface()
mongodb_interface = MongoDBInterface(config["MONGODB_CONNECTION_STRING"], config["MONGODB_DB_NAME"])
mongodb_interface.set_collection_mapping("Devices", config["MONGODB_DEVICES_COLLECTION_NAME"])
mongodb_interface.set_collection_mapping("Logs", config["MONGODB_LOGS_COLLECTION_NAME"])


## Single Retrival Requests
# Requests for following routes will be done via GET method and request through the url

@app.get("/v0/device/{object_id}")
async def device(object_id: str):
    response_wrapper = RetreivalResponse()
    try:
        result = await read_device_info(mongodb_interface,object_id) 
        if result is None:
            raise ItemNotFoundError
        result["_id"] = str(result["_id"])
        response_wrapper.set_status("success")
        response_wrapper.result = result
    except ItemNotFoundError:
        response_wrapper.set_status("item(s) not found")
    except Exception as e:
        response_wrapper.set_status("internal server error")
        print(e)
    finally:
        return response_wrapper.to_dict() 

@app.get("/v0/log/{object_id}")
async def log(object_id: str):
    response_wrapper = RetreivalResponse()
    try:
        result = await read_single_log(mongodb_interface,object_id)
        if result is None:
            raise ItemNotFoundError
        result["_id"] = str(result["_id"])
        result["timestamp"] = str(result["timestamp"]) 
        response_wrapper.set_status("success")
        response_wrapper.result = result
    except ItemNotFoundError:
        response_wrapper.set_status("item(s) not found")
    except Exception as e:
        response_wrapper.set_status("internal server error")
        print(e)
    finally:
        return response_wrapper.to_dict()

## Multi Retrival Routes
# Requests for following routes will be done via POST method and request through the body
#{
# "userSetLocation": "optional"
# "device" : optional (objectId)
# "sensors" : optional
# }

@app.post("/v0/device")
async def page_device(item: DeviceMultiRetreivalRequest):
    response_wrapper = RetreivalResponse()
    try:
        result = await read_paginated_device(mongodb_interface,item)
        response_wrapper.set_status("success")
        response_wrapper.result = result
    except Exception as e:
        response_wrapper.set_status("internal server error")
        print(e)
    finally:
        return response_wrapper.to_dict()

#{
# "datetime": optional
# "device" : optional (objectId)
# "sensor" : optional
# "cursor": optional (objectId)
# "limit": optional
# "dataFields" : [brightness, temperature, humidity, imageUrl, audioUrl] # all uses same method with different filter
#}

@app.post("/v0/log")
async def page_logs(item: TimeseriesMultiRetreivalRequest):
    response_wrapper = RetreivalResponse()
    try: 
        result = await read_paginated_logs(mongodb_interface,item)
        response_wrapper.set_status("success")
        response_wrapper.result = result
    except Exception as e:
        response_wrapper.set_status("internal server error")
        print(e)
    finally:
        return response_wrapper.to_dict()

# Upload Requests
# RabbitMq may be used to bulk upload to monogdb
# following endpoint route them into queue (logs likely)

@app.post("/upload/device")
async def upload_device(item: UploadDeviceRequest):
#register device to mongodb
    response_wrapper = MongodbUploadResponse() 
    try:
        result = await insert_device(mongodb_interface, item)
        if result is None:
            raise UpdateFailError
        if result["_id"] is not None:
            response_wrapper.insertedId = str(result["_id"]) 
        response_wrapper.set_status("success")
    except UpdateFailError:
        response_wrapper.set_status("update failed")
    except Exception as e:
        response_wrapper.set_status("internal server error")
        print(e)
    finally:
        return response_wrapper.to_dict()

@app.post("/upload/log")
async def upload_log(item: UploadLogRequest):
#validation will be done with sensor-field mapping
    response_wrapper = MongodbUploadResponse() 
    try:
        result = await insert_log(mongodb_interface, item)
        if result is None:
            raise UpdateFailError
        if result.inserted_id is not None:
            response_wrapper.insertedId = str(result.inserted_id)
        response_wrapper.set_status("success")
    except UpdateFailError:
        response_wrapper.set_status("update failed")
    except Exception as e:
        response_wrapper.set_status("internal server error")
        print(e)
    finally:
        return response_wrapper.to_dict()

@app.post("/upload/image")
#generate UUID with blob data using hash to ensure no duplicates
#metadata required to be called after upload (/upload/image/raw)
async def upload_image( file: Annotated[UploadFile, File()]):
        return {"hello": "world"}


@app.post("/upload/audio")
#generate UUID with blob data using hash to ensure no duplicates
#metadata required to be called after upload (/upload/audio/raw)
async def upload_audio( file: Annotated[UploadFile, File()]):
        return {"hello": "world"}


