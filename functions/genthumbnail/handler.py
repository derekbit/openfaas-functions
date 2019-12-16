# Usage
# curl http://127.0.0.1:31112/function/loadimage \
# -d "{\"bucket\": \"images\",\"source\": \"pexels_photo_532580.jpeg\",\"destination\": \"123456.jpeg\"}"
#
from minio import Minio
from minio.error import ResponseError
from PIL import Image
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
        mc.put_object(bucketname, filename,
            filecontent, len(filecontent.getvalue()), metadata=metadata)
    except ResponseError as err:
        print(err)
        raise ValueError("Failed to upload file to Minio")

def generate_thumbnail(filecontent, thumbsize):
    thumb = io.BytesIO()

    img = Image.open(filecontent)
    img.thumbnail(thumbsize)

    img.save(thumb, format='jpeg')
    return thumb;

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

    # Generate 100x100 and 800x800 thumbnails
    size = (100, 400, 800)
    prefix = ('s100', 'default', 's800')
    index = 0;
    for s in size:
        thumbcontent = generate_thumbnail(filecontent, (s,s))

        if thumbcontent is not None:
            to_s3(mc, thumbcontent, bucketname, ".@__thumb/" + prefix[index] + destination)
        else:
            raise ValueError("Failed to generate %s%s" % prefix[index], destination)

        index += 1
