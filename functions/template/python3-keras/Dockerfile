FROM openfaas/classic-watchdog:0.18.1 as watchdog

#FROM python:3-alpine
FROM ubuntu:18.04
#FROM centos:latest

# Allows you to add additional packages via build-arg
#ARG ADDITIONAL_PACKAGE

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog
#RUN apk --no-cache add ca-certificates ${ADDITIONAL_PACKAGE}
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-opencv
RUN pip3 install tensorflow keras numpy pandas opencv-python h5py Minio uuid simplejson requests

# Add non root user
RUN addgroup --system app
RUN adduser --system app --ingroup app

WORKDIR /home/app/
RUN mkdir -p /home/app/.keras/models
RUN apt-get install -y wget
RUN wget https://github.com/fchollet/deep-learning-models/releases/download/v0.5/inception_v3_weights_tf_dim_ordering_tf_kernels.h5 -P /home/app/.keras/models

COPY index.py           .
COPY requirements.txt   .

RUN chown -R app /home/app && \
  mkdir -p /home/app/python && chown -R app /home/app
USER app
ENV PATH=$PATH:/home/app/.local/bin:/home/app/python/bin/
ENV PYTHONPATH=$PYTHONPATH:/home/app/python

RUN pip3 install -r requirements.txt --target=/home/app/python

RUN mkdir -p function
RUN touch ./function/__init__.py

WORKDIR /home/app/function/
COPY function/requirements.txt	.

RUN pip3 install -r requirements.txt --target=/home/app/python

WORKDIR /home/app/

USER root

COPY function           function

RUN chown -R app:app ./ && \
  chmod -R 777 /home/app/python

USER app

ENV fprocess="python3 index.py"
EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
