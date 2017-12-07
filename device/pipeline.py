import cv2
import Queue
import numpy as np
import tensorflow as tf
import threading

import sys
sys.path.append('../')
#sys.path.append('../tfmodels/research/object_detection')

import config as cfg

from common import MyObject


class Pipeline(MyObject, threading.Thread):
    """Encapsulates a TensorFlow object detection graph."""

    QUEUE_TIMEOUT = 1.0

    def __init__(self, name, device):
        threading.Thread.__init__(self, name=name)
        self.device = device

        self.running = threading.Event()
        self.queue = Queue.Queue()

        path_to_cpkt = 'zoo/' + name + '/frozen_inference_graph.pb'

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(path_to_cpkt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=self.detection_graph)

            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        return

    def start(self):
        """Starts pipeline."""
        self.running.set()
        threading.Thread.start(self)
        return

    def run(self):
        """Pipeline thread target."""
        self.log().info('running pipeline')

        detection_graph = self.detection_graph
        image_tensor = self.image_tensor
        detection_boxes = self.detection_boxes
        detection_scores = self.detection_scores
        detection_classes = self.detection_classes
        num_detections = self.num_detections

        with detection_graph.as_default():
            while self.running.is_set():
                try:
                    job = self.queue.get(True, self.QUEUE_TIMEOUT)
                except Queue.Empty:
                    continue

                image = cv2.imdecode(job.data, cv2.IMREAD_UNCHANGED)
                image_np_expanded = np.expand_dims(image, axis=0)

                # Actual detection.
                (boxes, scores, classes, num) = self.sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})

                job.data = (boxes, scores, classes, num)
                self.device.send_result(job)

        self.sess.close()
        self.log().info('pipeline finished')
        return

    def stop(self):
        """Stops pipeline."""
        self.running.clear()
        return

