import cv2
import threading
import time

import sys
sys.path.append('../')

import config as cfg

from common import MyObject


class Camera(MyObject, threading.Thread):
    WAIT_TIMEOUT = 1.0

    def __init__(self, callback=None, source=0):
        threading.Thread.__init__(self, name='Camera')
        #self.daemon = ...

        self.callback = callback
        self.source = source

        self.frame_rate = 30.0
        self.compression = cfg.IMAGE_COMPRESSION

        self.image = None
        self.lock = threading.Lock()

        self.running = threading.Event()
        self.ready = threading.Event()
        return

    def start(self):
        self.log().info('starting camera')

        self.running.set()

        self.grabber = threading.Thread(name='Camera.grabber',
                                        target=self.frame_grabber)
        self.grabber.start()

        threading.Thread.start(self)
        return

    def stop(self):
        self.log().info('stopping camera')
        self.running.clear()
        self.grabber = None
        return

    def frame_grabber(self):
        self.log().debug('frame grabber starting')
        capture = cv2.VideoCapture(self.source)

        while self.running.is_set():
            if not capture.isOpened():
                self.log().error('capture not open')
                break

            status, image = capture.read()
            if not status:
                self.log().error('could not capture image')
                break

            with self.lock:
                self.image = image

            self.ready.set()

        capture.release()
        self.log().debug('frame grabber stopping')
        return

    def run(self):
        params = [cv2.IMWRITE_JPEG_QUALITY, self.compression]

        while self.running.is_set():
            self.ready.wait(self.WAIT_TIMEOUT)
            if not self.ready.is_set():
                continue

            with self.lock:
                image = self.image
                self.image = None

            self.ready.clear()

            if self.callback:
                ret, image_data = cv2.imencode('.jpg', image, params)
                if not ret:
                    self.log().error('could not compress image')
                    break

                self.callback(image_data)

            time.sleep(1.0/self.frame_rate)

        self.running.clear()
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'camera_output.log'

    logging.config.dictConfig(mylogcfg)

    def my_callback(image_data):
        image = cv2.imdecode(image_data, cv2.IMREAD_UNCHANGED)
        cv2.imwrite('test.jpg', image)

    try:
        camera = Camera(my_callback)
        camera.start()
        time.sleep(3)
        camera.stop()

    except KeyboardInterrupt:
        camera.stop()
