from minio import Minio
from minio.error import ResponseError
import simplejson as json
import requests
import numpy as np
import pandas as pd
import cv2
import os
import h5py
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.models import Model, load_model
from keras.applications.imagenet_utils import preprocess_input
from keras.utils.io_utils import HDF5Matrix

MIN_SEQ_LEN = 600
SUBSAMPLE   = 6

def get_secret(key):
    val = ""
    with open("/var/openfaas/secrets/" + key) as f:
        val = f.read()
    return val

def parse_event(payload):
    records  = payload['Records'][0]['s3']
    bucket   = records['bucket']['name']
    filename = records['object']['key']

    return bucket, filename

def download_from_s3(mc, bucket, filename):
    try:
        mc.fget_object(bucket, filename, "/tmp/" + filename)
    except ResponseError as err:
        print(err)
        raise ValueError("Failed to download file from Minio")

def preprocess_frame(frame):                                                                                                                                                
    frame = cv2.resize(frame, (299, 299))
    return preprocess_input(frame)

def encode_video(path):
    # Create base model
    base_model = InceptionV3(weights='imagenet', include_top=True)

    # Will extrace features at the final pooling layers
    model = Model(
        inputs = base_model.input,
        outputs = base_model.get_layer('avg_pool').output
    )

    cap = cv2.VideoCapture(path)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    num_groups = int(frame_count / MIN_SEQ_LEN)

    print("Number of groups: %d" % num_groups)

    features = []

    for i in range(num_groups):
        frames = []

        for j in (range(MIN_SEQ_LEN * i, MIN_SEQ_LEN * (i + 1))):
            if j % SUBSAMPLE == 0:
                ret, frame = cap.read()
                frame = preprocess_frame(frame)
                frames.append(frame)

        feature = model.predict(np.array(frames))
        features.append(feature)
        del frames[:]

    return np.array(features)

def handle(req):                                                                                                                                                            
    modelbucket = 'models'
    modelname   = 'Activity_Recognition.h5'

    payload = json.loads(req)

    mc = Minio(os.environ['minio_hostname'],
                access_key=get_secret('minio-access-key'),
                secret_key=get_secret('minio-secret-key'),
                secure=False)

    videobucket, videoname = parse_event(payload)

    download_from_s3(mc, videobucket, videoname)
    download_from_s3(mc, modelbucket, modelname)

    pretrained_model = load_model('/tmp/' + modelname)
    features = encode_video('/tmp/' + videoname)
    print('features shape: ', features.shape)

    predictions = pretrained_model.predict_classes(features)
    print(predictions)
