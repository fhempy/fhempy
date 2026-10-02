
# Object Detection
This module is used to detect objects within an image.

## Installation
```
sudo apt install libatlas3-base libsm6 libtiff5 libjasper1 libpng12-0 libavcodec-extra58 libavformat58 libswscale5
```

TensorFlow Lite is provided by LiteRT (`ai-edge-litert`), which is installed automatically.
Prebuilt packages are available for 64-bit Linux (x86_64 and aarch64), see:

https://ai.google.dev/edge/litert

## Usage
Stream
```
define obj_det fhempy object_detection stream "https://rbmn-live.akamaized.net/hls/live/2002825/geoSTVATweb/master.m3u8"
set obj_det start
```
Image
```
define obj_det fhempy object_detection image "FHEM/www/snapshot.jpg"
set obj_det start
```

## Attributes
 - detection_interval: Defines the detection interval in seconds (default: 2)
 - detection_threshold: Defines the threshold for detection (default: 0.6)