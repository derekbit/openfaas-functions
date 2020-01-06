# openfaas-functions

## Login before running the functions
### OpenFaas login
```
echo -n <admin password> | faas login --username=admin --password-stdin --gateway 127.0.0.1:31112
```

### Docker login
```
docker login
```

## Example functions
### helloworld

### getputobject
Add "RUN apk add jpeg-dev zlib-dev gcc musl-dev " into "template/python/Dockerfile"

### suspicious
## Reference
https://docs.min.io/docs/minio-bucket-notification-guide
https://www.roncrivera.io/post/serverless-functions-made-simple-with-openfaas/

## Steps
### Step 1:
Enable MinIO config's webhook

### Step 2:
root@dereksu-pc:/home/dereksu/faas# ./tools/mc event add minio/videos arn:minio:sqs::1:webhook --event put --suffix .mp4
Successfully added arn:minio:sqs::1:webhook

root@dereksu-pc:/home/dereksu/faas# ./tools/mc event list minio/videos
arn:minio:sqs::1:webhook   s3:ObjectCreated:*   Filter: suffix=".mp4"

### Event received by OpenFaaS
{"EventName":"s3:ObjectCreated:Put","Key":"videos/car3.mp4","Records":[{"eventVersion":"2.0","eventSource":"minio:s3","awsRegion":"","eventTime":"2020-01-06T02:30:45Z","eventName":"s3:ObjectCreated:Put","userIdentity":{"principalId":"admin"},"requestParameters":{"accessKey":"admin","region":"","sourceIPAddress":"192.168.81.59"},"responseElements":{"content-length":"0","x-amz-request-id":"15E72B568EF0E734","x-minio-deployment-id":"54fa9354-2d0b-44e0-a4e9-e771191dd5ad","x-minio-origin-endpoint":"http://10.0.3.2:9000"},"s3":{"s3SchemaVersion":"1.0","configurationId":"Config","bucket":{"name":"videos","ownerIdentity":{"principalId":"admin"},"arn":"arn:aws:s3:::videos"},"object":{"key":"car3.mp4","size":17149524,"eTag":"d6fc7a55508e63d6e98ddaffa1072a36-1","contentType":"video/mp4","userMetadata":{"content-type":"video/mp4"},"versionId":"1","sequencer":"15E72B56A2184285"}},"source":{"host":"192.168.81.59","port":"","userAgent":"MinIO (linux; amd64) minio-go/v6.0.39 mc/2019-10-09T22:54:57Z"}}]}

### Trigger Method
- Upload file by mc
../tools/mc cp /home/dereksu/car3.mp4 minio/videos
