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
