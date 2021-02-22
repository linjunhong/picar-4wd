# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to detect objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import cv2
import io
import re
import time

from annotation import Annotator

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


def load_labels(path):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = {}
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      if len(pair) == 2 and pair[0].strip().isdigit():
        labels[int(pair[0])] = pair[1].strip()
      else:
        labels[row_number] = pair[0].strip()
  return labels


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor


def detect_objects(interpreter, image, threshold):
  """Returns a list of detection results, each a dictionary of object info."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()

  # Get all output details
  boxes = get_output_tensor(interpreter, 0)
  classes = get_output_tensor(interpreter, 1)
  scores = get_output_tensor(interpreter, 2)
  count = int(get_output_tensor(interpreter, 3))

  results = []
  for i in range(count):
    if scores[i] >= threshold:
      result = {
          'bounding_box': boxes[i],
          'class_id': classes[i],
          'score': scores[i]
      }
      results.append(result)
  return results


def annotate_objects(annotator, results, labels):
  """Draws the bounding box and label for each object in the results."""
  for obj in results:
    # Convert the bounding box figures from relative coordinates
    # to absolute coordinates based on the original resolution
    ymin, xmin, ymax, xmax = obj['bounding_box']
    xmin = int(xmin * CAMERA_WIDTH)
    xmax = int(xmax * CAMERA_WIDTH)
    ymin = int(ymin * CAMERA_HEIGHT)
    ymax = int(ymax * CAMERA_HEIGHT)

    # Overlay the box, label, and score on the camera preview
    annotator.bounding_box([xmin, ymin, xmax, ymax])
    annotator.text([xmin, ymin],
                   '%s\n%.2f' % (labels[obj['class_id']], obj['score']))

def print_object_labels(results, labels):
    """Print object labels"""
    for obj in results:
        print("classid:", obj['class_id'], "label:", labels[obj['class_id']], "scores:", obj['score'])

def start_camera():
  camera = picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30)
  camera.rotation = 180

  return camera

def close_camera(camera):
  camera.close()

def capture_frame(camera):
  stream = io.BytesIO()
  for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
    stream.seek(0)
    image = Image.open(stream).convert('RGB').resize((input_width, input_height), Image.ANTIALIAS)
    stream.seek(0)
    stream.truncate()

  return image

def detect_new(arg_labels, arg_interpreter, arg_threshold, preview):
  labels = load_labels(arg_labels)
  interpreter = Interpreter(arg_interpreter, num_threads=2)
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  camera = start_camera()
  try:
    image = capture_frame(camera)
    
    start_time = time.monotonic()
    results = detect_objects(interpreter, image, arg_threshold)
    elapsed_ms = (time.monotonic() - start_time) * 1000

    print("Elapsed time (ms): ", elapsed_ms)
    print_object_labels(results, labels)

  finally:
    camera.close()

def detect(arg_labels, arg_interpreter, arg_threshold, preview):
  labels = load_labels(arg_labels)
  interpreter = Interpreter(arg_interpreter, num_threads=2)
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  with picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    camera.rotation = 180

    if (preview):
      camera.start_preview()

    try:
      stream = io.BytesIO()

      if (preview):
        annotator = Annotator(camera)

      for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):

        stream.seek(0)
        image = Image.open(stream).convert('RGB').resize((input_width, input_height), Image.ANTIALIAS)

        start_time = time.monotonic()
        results = detect_objects(interpreter, image, arg_threshold)
        elapsed_ms = (time.monotonic() - start_time) * 1000

        print("Elapsed time (ms): ", elapsed_ms)
        print_object_labels(results, labels)

        if (preview):
          annotator.clear()
          annotate_objects(annotator, results, labels)
          annotator.text([5, 0], '%.1fms' % (elapsed_ms))
          annotator.update()

        stream.seek(0)
        stream.truncate()

    finally:

      if (preview):
        camera.stop_preview()

def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  parser.add_argument(
      '--threshold',
      help='Score threshold for detected objects.',
      required=False,
      type=float,
      default=0.4)
  args = parser.parse_args()

  detect_new(args.labels, args.model, args.threshold, True)

if __name__ == '__main__':
  main()
