
import asyncio
import functools
import glob
import os

import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter, load_delegate

from .. import fhem, utils

class object_detection:

    def __init__(self, logger):
        self.logger = logger
        self._cwd_path = os.getcwd()
        obj_det_mod_dir = os.path.dirname(os.path.abspath(__file__))
        self._labels_path = os.path.join(obj_det_mod_dir, "labelmap.txt")
        self._graph_path = os.path.join(obj_det_mod_dir, "detect.tflite")
        self._min_conf_threshold = float(0.6)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 4:
            return "Usage: define obj_detection PythonModule object_detection <IMG_LOCATION>"
        if args[3][0] == "/":
            self._image_path = args[3]
        else:
            self._image_path = os.path.join(self._cwd_path, args[3])
        self.logger.debug(f"Load image: {self._image_path}")
        return ""

    def run_object_detection(self):
        detected_objects = []
        # Load the label map
        with open(self._labels_path, 'r') as f:
            labels = [line.strip() for line in f.readlines()]

        # Have to do a weird fix for label map if using the COCO "starter model" from
        # https://www.tensorflow.org/lite/models/object_detection/overview
        # First label is '???', which has to be removed.
        if labels[0] == '???':
            del(labels[0])
        interpreter = Interpreter(model_path=self._graph_path)
        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]
        floating_model = (input_details[0]['dtype'] == np.float32)
        input_mean = 127.5
        input_std = 127.5

        # Load image and resize to expected shape [1xHxWx3]
        image_path = self._image_path
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape 
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > self._min_conf_threshold) and (scores[i] <= 1.0)):
    
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                
                cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
    
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                detected_objects.append({"object": object_name, "score": int(scores[i]*100)})

                # Draw label
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

                # output file with object rectangle and text
                #cv2.imwrite(self._output_file, image)
        return detected_objects

    # FHEM FUNCTION
    async def Undefine(self, hash):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        set_list_conf = {
           "detectnow": { }
        }
        return await utils.handle_set(set_list_conf, self, hash, args, argsh)

    async def set_detectnow(self, hash):
        asyncio.create_task(self.detect_objects())
        return ""

    async def detect_objects(self):
        detected_objects = await utils.run_blocking(functools.partial(self.run_object_detection))
        all_objects = {}
        await fhem.CommandDeleteReading(self.hash, self.hash["NAME"] + " object_.*")
        await fhem.readingsBeginUpdate(self.hash)
        for obj in detected_objects:
            obj_name = obj['object']
            obj_score = obj['score']
            if obj_name not in all_objects:
                all_objects[obj_name] = 0
            all_objects[obj_name] += 1
            await fhem.readingsBulkUpdate(self.hash, "object_" + obj_name, obj_score)
        for obj_name in all_objects:
            await fhem.readingsBulkUpdate(self.hash, "object_count_" + obj_name, all_objects[obj_name])
        await fhem.readingsBulkUpdate(self.hash, "state", ",".join(set(all_objects)))
        await fhem.readingsEndUpdate(self.hash, 1)
