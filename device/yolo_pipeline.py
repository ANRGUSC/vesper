import cv2
import Queue
import thread
import threading

import sys
sys.path.append('./')

import config as cfg

from common import MyObject

sys.path.append('./darknet/python')
import darknet

class YoloPipeline(MyObject, threading.Thread):
    """Encapsulates a YOLO object detection network."""

    QUEUE_TIMEOUT = 1.0

    def __init__(self, name, device):
        threading.Thread.__init__(self, name=name)
        self.device = device

        if name == 'tiny_yolo':
            self.net = darknet.load_net("darknet/cfg/tiny-yolo-voc.cfg", "zoo/tiny-yolo-voc.weights", 0)
            self.meta = darknet.load_meta("darknet/cfg/voc.data")

        elif name == 'yolo_v2':
            self.net = darknet.load_net("darknet/cfg/yolo.cfg", "zoo/yolo.weights", 0)
            self.meta = darknet.load_meta("darknet/cfg/coco.data")

        else:
            self.log().critical("unknown pipeline '%s'", name)
            thread.interrupt_main()
            return

        self.running = threading.Event()
        self.queue = Queue.Queue()
        return

    def start(self):
        """Starts pipeline."""
        self.running.set()
        threading.Thread.start(self)
        return

    def run(self):
        """Pipeline thread target."""
        self.log().info('running pipeline')

        while self.running.is_set():
            try:
                job = self.queue.get(True, self.QUEUE_TIMEOUT)
            except Queue.Empty:
                continue

            image = cv2.imdecode(job.data, cv2.IMREAD_UNCHANGED)
            result = darknet.detect(self.net, self.meta, image)

            job.data = result
            self.device.send_result(job)

        self.log().info('pipeline finished')
        return

    def stop(self):
        """Stops pipeline."""
        self.running.clear()
        return


if __name__ == '__main__':
    image = cv2.imread('../darknet/data/giraffe.jpg')

    #net = darknet.load_net("darknet/cfg/tiny-yolo-voc.cfg", "zoo/tiny-yolo-voc.weights", 0)
    #meta = darknet.load_meta("darknet/cfg/voc.data")
    net = darknet.load_net("darknet/cfg/yolo.cfg", "zoo/yolo.weights", 0)
    meta = darknet.load_meta("darknet/cfg/coco.data")

    print darknet.detect(net, meta, image)
