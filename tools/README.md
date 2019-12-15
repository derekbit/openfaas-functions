# Tools

## mc: MinIO Client

https://docs.min.io/docs/minio-client-complete-guide

### Usage
- Login
```
# ./mc config host add minio http://192.168.81.104:9000 admin qnap1234
Added `minio` successfully.
```

- List files in one bucket
```
./mc ls minio/helloworld
```

- Show the attributes and metadata of one file
```
# ./mc stat minio/helloworld/.@__thumb/s100pexels_photo_1050584.jpeg
Name      : s100pexels_photo_1050584.jpeg
Date      : 2019-12-15 14:10:54 CST 
Size      : 3.9 KiB 
ETag      : 2db05c59437379d47df7f5ac1ed09c2b-1 
Type      : file 
Metadata  :
  Content-Type         : image/jpeg 
  X-Amz-Meta-File-Mtime: 1570519994 
```
