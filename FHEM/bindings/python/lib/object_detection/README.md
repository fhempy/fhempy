
# Object Detection
This module is used to detect objects within an image.

## Installation
```
sudo apt install libatlas3-base libsm6 libtiff5 libjasper1 libpng12-0 libavcodec-extra58 libavformat58 libswscale5
```

Install TensorFlow Lite, the link below is for RPi ARM32 Python 3.7
```
sudo pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
```
for other configuration please find the proper link here:

https://www.tensorflow.org/lite/guide/python

## Usage
Stream
```
define obj_det PythonModule object_detection stream "https://rbmn-live.akamaized.net/hls/live/2002825/geoSTVATweb/master.m3u8"
set obj_det start
```
Image
```
define obj_det PythonModule object_detection image "FHEM/www/snapshot.jpg"
set obj_det start
```

## Attributes
 - detection_interval: Defines the detection interval in seconds (default: 2)
 - detection_threshold: Defines the threshold for detection (default: 0.6)