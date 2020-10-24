
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
```
define obj_det PythonModule object_detection "FHEM/www/snapshot.jpg"
set obj_det detectnow
```