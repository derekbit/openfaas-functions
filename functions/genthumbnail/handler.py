# Usage
# curl http://127.0.0.1:31112/function/loadimage \
# -d "{\"bucket\": \"images\",\"source\": \"appetite_apple_calories_catering_161615.jpeg\",\"destination\": \"appetite_apple_calories_catering_161615.jpeg\"}"
#
from minio import Minio
from minio.error import ResponseError
from PIL import Image
import requests
import json
import os
import io
import time
import calendar

def get_mtime_and_content_type(mc, bucketname, filename):
    try:
        obj = mc.stat_object(bucketname, filename)
        # struct_time in UTC, seconds since the epoch
        mtime = calendar.timegm(obj.last_modified)
        # struct_time in local time, seconds since the epoch
        mtime = time.mktime(obj.last_modified)

        return int(mtime), obj.content_type
    except ResponseError as err:
        print(err)
        return -1

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

def to_s3(mc, filecontent, bucketname, filename, content_type, mtime):
    metadata = {"X-Amz-Meta-file-mtime": str(mtime)}

    try:
        filecontent.seek(0)
        mc.put_object(bucketname, filename,
            filecontent, len(filecontent.getvalue()),
            content_type=content_type, metadata=metadata)
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

    mtime, content_type = get_mtime_and_content_type(mc, bucketname, source)
    if mtime is -1:
        raise ValueError("Failed to get mtime from Minio")

    # Generate 100x100 and 800x800 thumbnails
    size = (100, 400, 800)
    prefix = ('s100', 'default', 's800')
    index = 0;
    for s in size:
        thumbcontent = generate_thumbnail(filecontent, (s,s))

        if thumbcontent is not None:
            to_s3(mc, thumbcontent, bucketname, ".@__thumb/" + prefix[index] + destination, content_type, mtime)
        else:
            raise ValueError("Failed to generate %s%s" % prefix[index], destination)

        index += 1
