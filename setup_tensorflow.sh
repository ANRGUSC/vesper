#!/usr/bin/env bash

set -eux

ROOT=`pwd`

# Compile protobuf files
cd tfmodels/research
protoc object_detection/protos/*.proto --python_out=.

# Download models from Tensorflow detection model zoo
cd $ROOT
mkdir -p zoo
cd zoo

SSD_MOBILENET="ssd_mobilenet_v1_coco_2017_11_17"
wget -nc http://download.tensorflow.org/models/object_detection/${SSD_MOBILENET}.tar.gz
tar -xf ${SSD_MOBILENET}.tar.gz ${SSD_MOBILENET}/frozen_inference_graph.pb

SSD_INCEPTION="ssd_inception_v2_coco_2017_11_17"
wget -nc http://download.tensorflow.org/models/object_detection/${SSD_INCEPTION}.tar.gz
tar -xf ${SSD_INCEPTION}.tar.gz ${SSD_INCEPTION}/frozen_inference_graph.pb
