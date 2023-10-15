import boto3
import hashlib
from botocore.exceptions import ClientError
from typing import Optional
from roomsense2.errors import * 
from fastapi import UploadFile

class S3Interface:

    collectionMapping : dict[str,str] = dict()
    region: Optional[str] = None

    def __init__(self, access_key_id:str, secret_access_key:str, region:str | None):
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        if region is not None:
            self.region = region
    
    def set_collection_mapping(self, key:str, value:str):
        self.collectionMapping[key] = value


## helper methods that uses mongodb interface for local application
async def upload_s3_image(s3_interface:S3Interface, file_obj: UploadFile):
    return await upload_s3_file(s3_interface,"Images", file_obj)

async def upload_s3_audio(s3_interface:S3Interface, file_obj: UploadFile): 
    return await upload_s3_file(s3_interface,"Audios", file_obj)

async def upload_s3_file(s3_interface:S3Interface,bucket_key:str, file_obj: UploadFile):
    s3 = s3_interface.client
    bucket_name = s3_interface.collectionMapping[bucket_key]
    try:
        new_file_name = f"{await generate_hash(file_obj)}.{get_file_extension(file_obj)}"
        s3.put_object(Body=file_obj.file,Bucket=bucket_name,Key=new_file_name)
        return dynamic_aws_url(bucket_name, new_file_name, s3_interface.region)
    except ClientError as e:
        print(f"Error uploading log to S3 bucket {bucket_name}: {e}")
        raise UploadFailError
        
#general s3 helpers
def dynamic_aws_url(bucket_name:str, file_name:str, region:str| None):
    if region is not None:
        return f"https://{bucket_name}.s3.{region}.amazonaws.com/{file_name}"
    return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

def get_file_extension(file_obj):
    return file_obj.filename.split(".")[-1]

#helper for generating has from file data
async def generate_hash(file_obj):

    hash_obj = hashlib.sha256()
    while True:
        data = file_obj.file.read(1024)
        if not data:
            break
        hash_obj.update(data)
    await file_obj.seek(0)   
    return hash_obj.hexdigest()