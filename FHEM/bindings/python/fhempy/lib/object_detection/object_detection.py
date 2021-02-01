import asyncio
import concurrent
import functools
import glob
import os
import time
from threading import Thread

import cv2
import numpy as np
import tflit
from fhempy.lib.generic import FhemModule
from tflite_runtime.interpreter import Interpreter, load_delegate

from .. import fhem, utils


class object_detection(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.loop = asyncio.get_event_loop()
        self._cwd_path = os.getcwd()
        obj_det_mod_dir = os.path.dirname(os.path.abspath(__file__))
        self._labels_path = os.path.join(obj_det_mod_dir, "labelmap.txt")
        self._graph_path = os.path.join(obj_det_mod_dir, "detect.tflite")
        self._detection_task = None
        self._prev_objects = None
        self._stop_detection = False
        self._attr_detection_interval = 2
        self._attr_detection_threshold = 0.6
        self._attr_list = {
            "detection_interval": {"default": 2, "format": "float"},
            "detection_threshold": {"default": 0.6, "format": "float"},
        }
        self.set_attr_config(self._attr_list)
        set_list_conf = {"start": {}, "detect_once": {}, "stop": {}}
        self.set_set_config(set_list_conf)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 5:
            return "Usage: define obj_detection PythonModule object_detection <image/stream> <LOCATION>"
        if args[3] == "image":
            if args[4][0] == "/":
                self._source_uri = args[4]
            else:
                self._source_uri = os.path.join(self._cwd_path, args[4])
        else:
            self._source_uri = args[4]
        self._source_type = args[3]

        self.logger.debug(f"Source URI: {self._source_uri}")
        await fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1)

    def run_stream_object_detection(self):
        # Load the label map
        with open(self._labels_path, "r") as f:
            labels = [line.strip().replace(" ", "_") for line in f.readlines()]

        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if labels[0] == "???":
            del labels[0]
        interpreter = Interpreter(model_path=self._graph_path)
        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]["shape"][1]
        width = input_details[0]["shape"][2]
        floating_model = input_details[0]["dtype"] == np.float32
        input_mean = 127.5
        input_std = 127.5

        # Initialize frame rate calculation
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()

        # resolution
        imW = 1280
        imH = 720

        # Initialize video stream
        videostream = VideoStream(
            self._source_uri, resolution=(imW, imH), framerate=30, loop=self.loop
        ).start()
        time.sleep(1)

        # for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        while True:

            try:
                # Start timer (for calculating frame rate)
                # t1 = cv2.getTickCount()

                # Grab frame from video stream
                frame1 = videostream.read()
                if frame1 is None:
                    continue

                # Acquire frame and resize to expected shape [1xHxWx3]
                frame = frame1.copy()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (width, height))
                input_data = np.expand_dims(frame_resized, axis=0)

                # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
                if floating_model:
                    input_data = (np.float32(input_data) - input_mean) / input_std

                # Perform the actual detection by running the model with the image as input
                interpreter.set_tensor(input_details[0]["index"], input_data)
                interpreter.invoke()

                # Retrieve detection results
                boxes = interpreter.get_tensor(output_details[0]["index"])[
                    0
                ]  # Bounding box coordinates of detected objects
                classes = interpreter.get_tensor(output_details[1]["index"])[
                    0
                ]  # Class index of detected objects
                scores = interpreter.get_tensor(output_details[2]["index"])[
                    0
                ]  # Confidence of detected objects
                # num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

                detected_objects = []
                # Loop over all detections and draw detection box if confidence is above minimum threshold
                for i in range(len(scores)):
                    if (scores[i] > self._attr_detection_threshold) and (
                        scores[i] <= 1.0
                    ):

                        # Get bounding box coordinates and draw box
                        # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                        # ymin = int(max(1,(boxes[i][0] * imH)))
                        # xmin = int(max(1,(boxes[i][1] * imW)))
                        # ymax = int(min(imH,(boxes[i][2] * imH)))
                        # xmax = int(min(imW,(boxes[i][3] * imW)))

                        # cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                        # Draw label
                        object_name = labels[
                            int(classes[i])
                        ]  # Look up object name from "labels" array using class index
                        label = "%s: %d%%" % (
                            object_name,
                            int(scores[i] * 100),
                        )  # Example: 'person: 72%'
                        # labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                        # label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                        # cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                        # cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

                        detected_objects.append(
                            {"object": object_name, "score": int(scores[i] * 100)}
                        )

                asyncio.run_coroutine_threadsafe(
                    self.update_readings(detected_objects), self.loop
                ).result()

                if self._stop_detection:
                    asyncio.run_coroutine_threadsafe(
                        fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1),
                        self.loop,
                    ).result()
                    videostream.stop()
                    return

                # Draw framerate in corner of frame
                # cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

                # All the results have been drawn on the frame, so it's time to display it.
                # cv2.imshow('Object detector', frame)

                # Calculate framerate
                # t2 = cv2.getTickCount()
                # time1 = (t2-t1)/freq
                # frame_rate_calc= 1/time1
                time.sleep(self._attr_detection_interval)
            except asyncio.CancelledError:
                videostream.stop()
                return

    def run_image_object_detection(self):
        detected_objects = []
        # Load the label map
        with open(self._labels_path, "r") as f:
            labels = [line.strip() for line in f.readlines()]

        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if labels[0] == "???":
            del labels[0]
        interpreter = Interpreter(model_path=self._graph_path)
        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]["shape"][1]
        width = input_details[0]["shape"][2]
        floating_model = input_details[0]["dtype"] == np.float32
        input_mean = 127.5
        input_std = 127.5

        # Load image and resize to expected shape [1xHxWx3]
        image_path = self._source_uri
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]["index"])[
            0
        ]  # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]["index"])[
            0
        ]  # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]["index"])[
            0
        ]  # Confidence of detected objects
        # num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if (scores[i] > self._attr_detection_threshold) and (scores[i] <= 1.0):

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                object_name = labels[
                    int(classes[i])
                ]  # Look up object name from "labels" array using class index
                detected_objects.append(
                    {"object": object_name, "score": int(scores[i] * 100)}
                )

                # Draw label
                label = "%s: %d%%" % (
                    object_name,
                    int(scores[i] * 100),
                )  # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )  # Get font size
                label_ymin = max(
                    ymin, labelSize[1] + 10
                )  # Make sure not to draw label too close to top of window
                cv2.rectangle(
                    image,
                    (xmin, label_ymin - labelSize[1] - 10),
                    (xmin + labelSize[0], label_ymin + baseLine - 10),
                    (255, 255, 255),
                    cv2.FILLED,
                )  # Draw white box to put label text in
                cv2.putText(
                    image,
                    label,
                    (xmin, label_ymin - 7),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    2,
                )  # Draw label text

                # output file with object rectangle and text
                # cv2.imwrite(self._output_file, image)
        return detected_objects

    async def set_start(self, hash, params):
        self._stop_detection = False
        await self.start_detection()

    async def set_detect_once(self, hash, params):
        self._stop_detection = True
        await self.start_detection()

    async def start_detection(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "running", 1)
        if self._source_type == "image":
            self.create_async_task(self.image_detect_objects_loop())
        else:
            self._detection_task = utils.run_blocking_task(
                functools.partial(self.run_stream_object_detection)
            )
        return ""

    async def set_stop(self, hash, params):
        self._stop_detection = True

    async def image_detect_objects_loop(self):
        while True:
            await self.image_detect_objects()
            if self._stop_detection:
                break
            await asyncio.sleep(self._attr_detection_interval)
        await fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1)

    async def image_detect_objects(self):
        detected_objects = await utils.run_blocking(
            functools.partial(self.run_image_object_detection)
        )
        await self.update_readings(detected_objects)

    async def update_readings(self, detected_objects):
        try:
            all_objects = {}
            curr_objects = {}
            if self._prev_objects is None:
                await fhem.CommandDeleteReading(
                    self.hash, self.hash["NAME"] + " object_.*"
                )

            await fhem.readingsBeginUpdate(self.hash)
            for obj in detected_objects:
                obj_name = obj["object"]
                obj_score = obj["score"]
                if obj_name not in all_objects:
                    all_objects[obj_name] = 0
                all_objects[obj_name] += 1
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "object_" + obj_name, obj_score
                )
            for obj_name in all_objects:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "object_count_" + obj_name, all_objects[obj_name]
                )
                curr_objects[obj_name] = all_objects[obj_name]

            # set readings to 0 for objects which were not found
            if self._prev_objects is None:
                set_0_readings = {}
            else:
                set_0_readings = set(self._prev_objects) - set(curr_objects)
            for set_0_reading in set_0_readings:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "object_" + set_0_reading, 0
                )
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "object_count_" + set_0_reading, 0
                )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "objects_detected", ",".join(set(all_objects))
            )
            await fhem.readingsEndUpdate(self.hash, 1)

            self._prev_objects = curr_objects
        except Exception:
            self.logger.exception("Failed to update readings")


# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming"""

    def __init__(self, source_uri, resolution=(640, 480), framerate=30, loop=None):
        self.loop = loop
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(source_uri)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        ret = self.stream.set(cv2.CAP_PROP_FPS, framerate)
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        self._task = self.loop.create_task(self.update_task())
        return self

    async def update_task(self):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await self.loop.run_in_executor(pool, functools.partial(self.update))

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            try:
                # If the camera is stopped, stop the thread
                if self.stopped:
                    # Close camera resources
                    self.stream.release()
                    return

                # Otherwise, grab the next frame from the stream
                (self.grabbed, self.frame) = self.stream.read()
            except asyncio.CancelledError:
                self.stream.release()
                return

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True
