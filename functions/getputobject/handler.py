# Usage
# curl http://127.0.0.1:31112/function/loadimage \
# -d "{\"bucket\": \"images\",\"source\": \"pexels_photo_532580.jpeg\",\"destination\": \"123456.jpeg\"}"
#
from minio import Minio
from minio.error import ResponseError
import requests
import json
import os
import io

def from_s3(mc, bucketname, filename):
    try:
        data = mc.get_object(bucketname, filename)
        filecontent = io.BytesIO()
        for d in data.stream(32*1024):
            filecontent.write(d)
        return filecontent
    except ResponseError as err:
        print(err)
        return None

def to_s3(mc, filecontent, bucketname, filename):
    metadata = {"X-Amz-Meta-Hello": "World"}

    try:
        filecontent.seek(0)
        mc.put_object(bucketname, filename, filecontent, len(filecontent.getvalue()), metadata=metadata)
    except ResponseError as err:
        print(err)
        raise ValueError("Failed to upload file to Minio")

def handle(st):
    req = json.loads(st)
    bucketname = "images"

    bucketname = req["bucket"]
    source = req["source"]
    destination = req["destination"]

    mc = Minio(os.environ['minio_hostname'],
                access_key=os.environ['minio_access_key'],
                secret_key=os.environ['minio_secret_key'],
                secure=False)
    if mc is None:
        raise ValueError("Failed to connect to Minio")

    filecontent = from_s3(mc, bucketname, source)
    if filecontent is None:
        raise ValueError("Failed to get file from Minio")
    
    to_s3(mc, filecontent, bucketname, destination)
