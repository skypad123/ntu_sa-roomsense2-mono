import motor.motor_asyncio
from roomsense2.common_types import TimeseriesLog, DeviceMeta
from roomsense2.fmt import TimeseriesMultiRetreivalRequest, DeviceMultiRetreivalRequest
from bson import ObjectId, json_util

class MongoDBInterface:

    collectionMapping : dict[str,str] = dict()

    def __init__(self, connectionString:str, databaseName:str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connectionString)
        self.database = self.client[databaseName] 
    
    def set_collection_mapping(self, key:str, value:str):
        self.collectionMapping[key] = value

## helper methods that uses mongodb interface for local application


async def read_paginated_device(db_interface:MongoDBInterface, query: DeviceMultiRetreivalRequest):
    
    def query_to_filter(query: DeviceMultiRetreivalRequest):
        filter = dict()
        if query.device is not None:
            filter["device"] = query.device
        if query.userSetLocation is not None:
            filter["userSetLocation"] = query.userSetLocation
        if query.sensor is not None:
            filter["sensors"] = {"$all": query.sensor}

        print(f"searching mongodb devices collection with filter: {filter}")
        return  filter

    coll = db_interface.database[db_interface.collectionMapping["Devices"]]
    filter = query_to_filter(query)

    mongo_cursor = coll.find(filter)
    if query.cursor is not None:
        mongo_cursor = mongo_cursor.skip(query.cursor)
    if query.limit is not None:
        mongo_cursor = mongo_cursor.limit(query.limit)
    else:
        mongo_cursor = mongo_cursor.limit(50)

    page = list()
    async for doc in mongo_cursor:
        python_dict = json_util.loads(json_util.dumps(doc))
        python_dict["_id"] = str(python_dict["_id"])
        page.append(python_dict)

    ret=dict()
    ret["data"] = page
    page_size = len(page)
    match (query.cursor, query.limit):
        case (None, None):
            ret["cursor"] = None if page_size < 50 else page_size
        case (None, limit):
            ret["cursor"] = None if page_size < limit else page_size
        case (cursor, None):
            ret["cursor"] = None if page_size < 50 else cursor + page_size
        case (cursor, limit):
            ret["cursor"] = None if page_size < limit else cursor + limit

    return ret

# reading paginated Log data by filter and cursor
async def read_paginated_logs(db_interface:MongoDBInterface, query: TimeseriesMultiRetreivalRequest):
    def query_to_filter(query: TimeseriesMultiRetreivalRequest):
        filter = dict()
        if query.device is not None:
            filter["metadata.device"] = query.device
        if query.datetime is not None:
            filter["timestamp"] = {"$lte": query.datetime}
        if query.sensor is not None:
            filter["metadata.sensor"] = {"$in": query.sensor}
        if query.dataFields is not None: 
            for field in query.dataFields:
                filter[f"data.{field}"] = {"$exists": True }
        print(f"searching mongodb devices collection with filter: {filter}")
        return  filter

    coll = db_interface.database[db_interface.collectionMapping["Logs"]]
    filter = query_to_filter(query)

    mongo_cursor = coll.find(filter)
    if query.cursor is not None:
        mongo_cursor = mongo_cursor.skip(query.cursor)
    if query.limit is not None:
        mongo_cursor = mongo_cursor.limit(query.limit)
    else:
        mongo_cursor = mongo_cursor.limit(50)

    page = list()
    async for doc in mongo_cursor:
        python_dict = json_util.loads(json_util.dumps(doc))
        python_dict["_id"] = str(python_dict["_id"])
        python_dict["timestamp"] = str(python_dict["timestamp"])
        page.append(python_dict)

    ret=dict()
    ret["data"] = page
    page_size = len(page)
    match (query.cursor, query.limit):
        case (None, None):
            ret["cursor"] = None if page_size < 50 else page_size
        case (None, limit):
            ret["cursor"] = None if page_size < limit else page_size
        case (cursor, None):
            ret["cursor"] = None if page_size < 50 else cursor + page_size
        case (cursor, limit):
            ret["cursor"] = None if page_size < limit else cursor + limit

    return ret

# reading device data
async def read_device_info(db_interface:MongoDBInterface, object_id:str):
    object_id = ObjectId(object_id)
    coll = db_interface.database[db_interface.collectionMapping["Devices"]]
    return await coll.find_one({"_id": object_id})

# reading single Log data by ObjectId
async def read_single_log(db_interface:MongoDBInterface, object_id:str):
    object_id = ObjectId(object_id)
    coll = db_interface.database[db_interface.collectionMapping["Logs"]]
    return await coll.find_one({"_id": object_id})

# inserting/updating Device data
async def insert_device(db_interface:MongoDBInterface, data: DeviceMeta):
    print(f"inserting data into devices collection: {data}")
    coll = db_interface.database[db_interface.collectionMapping["Devices"]]
    return await coll.find_one_and_replace({"device": data.device},data.to_dict(),{"upsert":True})

# inserting/updating Log data
async def insert_log(db_interface:MongoDBInterface, data: TimeseriesLog):
    print(f"inserting data into logs collection: {data}")
    coll = db_interface.database[db_interface.collectionMapping["Logs"]]
    return await coll.insert_one(data.to_dict())



