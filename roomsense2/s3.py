import boto3
from botocore.config import Config

class S3Interface:

    client : boto3.client

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id='AKIASZWP5QRVTRH7TB5K',
            aws_secret_access_key='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',
        )





