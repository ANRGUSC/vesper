import copy
import cv2
import numpy as np
import Queue
import thread
import time

import sys
sys.path.append('../')

import config as cfg

from common import Job, Message
from common import Monitor
from common import Service
from dashboard import Dashboard
from network import Server
from node import Node


class Dispatcher(Service):
    """Handles communication from drone and devices."""

    ITEM_FPS        = 'FPS'
    ITEM_MAKESPAN   = '~Makespan'
    ITEM_THROUGHPUT = '~Throughput'

    def __init__(self, controller=None):
        Service.__init__(self, 'dispatcher')

        self.handlers[Message.TYPE_LOGIN] = self.handle_login
        self.handlers[Message.TYPE_IMAGE] = self.handle_image
        self.handlers[Message.TYPE_RESULT] = self.handle_result

        self.server = Server(self, cfg.SERVER_PORT)
        self.protocols = {}

        self.nodes = {}

        if cfg.DASHBOARD:
            self.dashboard = Dashboard()
            self.dashboard.start()

        else:
            self.dashboard = None

        measure_period = float(cfg.CONTROLLER_LOOP_TIME)/cfg.MEASURES_PER_LOOP
        self.monitor = Monitor(self.process_measurements, measure_period)
        self.monitor.register_item(self.ITEM_FPS, Monitor.ITEM_RATE)
        self.monitor.register_item(self.ITEM_MAKESPAN, Monitor.ITEM_AVG)
        self.monitor.register_item(self.ITEM_THROUGHPUT, Monitor.ITEM_RATE)

        self.controller = controller
        self.controller.dashboard = self.dashboard
        self.controller.dispatcher = self

        self.dashboard.controller = controller

        self.imagebuf = Queue.Queue()   # Buffer of encoded images
                                        # (time stamp, image data)

        # Initialize probe to blank image
        self.probe_image = self.generate_probe_image()

        self.tokens = Queue.Queue()
        self.job_id = 0

        self.sub_loop = 0
        return

    def handle_login(self, protocol, msg):
        """Handles device logins."""
        name = msg.name
        self.log().info("'%s' login", name)

        protocol.name = name
        self.protocols[name] = protocol

        if not self.controller is None:
            self.controller.logon(name)

        if not name == cfg.CAMERA_NAME:
            self.nodes[name] = Node(name)
            self.tokens.put(name)

        return

    def handle_image(self, protocol, msg):
        """Handles images."""

        if self.monitor:
            self.monitor.update_item(self.ITEM_FPS, 1)

        if self.dashboard:
            image = cv2.imdecode(msg.data, cv2.IMREAD_UNCHANGED)
            self.dashboard.put_image(image)

        self.imagebuf.put((time.time(), msg.data))
        self.probe_image = msg.data
        return

    def handle_result(self, protocol, msg):
        """Handles result."""
        name = protocol.name

        job = msg.data
        job.end = time.time()

        if job.probe:
            prefix = 'probe '
        else:
            prefix = ''

        self.log().info("%sjob %d completed by '%s'", prefix, job.job_id, name)
        self.log().debug(job)

        # Update system stats
        makespan = job.end - job.start
        proc_time = job.left - job.arrived
        rtt = makespan - proc_time

        self.log().debug('%sjob %d makespan: %0.6f', prefix, job.job_id, makespan)
        self.log().debug('%sjob %d proc_time: %0.6f', prefix, job.job_id, proc_time)
        self.log().debug('%sjob %d rtt: %0.6f', prefix, job.job_id, rtt)

        now = job.end

        # Ignore probe jobs
        if not job.probe:
            self.monitor.update_item(self.ITEM_MAKESPAN, makespan)

            if job.deadline >= now:
                self.monitor.update_item(self.ITEM_THROUGHPUT, 1)


        proc_rate = cfg.PIPELINES[job.pipeline][1]/proc_time

        # Update device stats
        node = self.nodes[name]
        with node.lock:
            node.processing_rate.add(proc_rate)
            node.rtt.add(rtt)

        self.log().debug('node updated %s', node)

        self.tokens.put(name)
        return

    def process_measurements(self, values):
        """Handles measurements from a Monitor."""
        self.log().debug('measurements: %s', values)

        self.sub_loop += 1
        self.sub_loop %= cfg.MEASURES_PER_LOOP

        if self.controller:
            self.controller.put_metrics(values)

            if self.sub_loop == 0:
                self.controller.loop()

            cvalues = self.controller.get_values()
            values.update(cvalues)

        values['nodes'] = self.nodes
        values['imagebuf'] = self.imagebuf.qsize()

        if self.dashboard:
            self.dashboard.put_values(values)

        return

    def start(self):
        """Starts the dispatcher server."""
        self.log().info('starting dispatcher')

        if self.monitor:
            self.monitor.start()

        if self.controller:
            self.controller.start()

        self.server.run()   # Blocking call
        return

    def stop(self):
        """Stops the dispatcher server."""
        self.log().info('stopping dispatcher')

        if self.monitor:
            self.monitor.stop()

        if self.dashboard:
            self.dashboard.stop()

        if self.controller:
            self.controller.stop()

        self.server.stop()
        return

    def disconnected(self, protocol):
        """Handles device disconnections."""
        name = protocol.name
        del self.protocols[name]
        self.log().info("'%s' disconnected", name)

        if not self.controller is None:
            self.controller.logoff(name)

        if not name == cfg.CAMERA_NAME:
            del self.nodes[name]

        return

    def send_params(self, name, params):
        """Sends settings to client."""

        protocol = self.protocols.get(name)
        if not protocol is None:
            msg = Message(self.name, Message.TYPE_PARAMS, params)
            protocol.send(msg)

        else:
            self.log().warn("send_params: protocol '%s' not found", name)

        return

    def next_job_id(self):
        """Returns next job id."""
        job_id = self.job_id
        self.job_id += 1
        return job_id

    def generate_probe_image(self):
        """Generate random blank image for probing."""
        # Note: Due to the randomness, this will likely be larger in (encoded)
        # size than an image from the drone

        blank = np.random.randint(0, 256, (480, 640, 3), np.uint8)
        params = [cv2.IMWRITE_JPEG_QUALITY, 50]

        ret, image_data = cv2.imencode('.jpg', blank, params)
        if ret:
            return image_data
        else:
            thread.interrupt_main()

    def probe(self, name, pipeline):
        """Sends fake job to a device to probe."""

        protocol = self.protocols.get(name)
        if protocol:
            job = Job(self.next_job_id(), pipeline, self.probe_image, True)
            msg = Message(self.name, Message.TYPE_JOB, job)

            self.log().info("sending job %d to '%s'", job.job_id, name)
            self.log().debug('%s', job)
            protocol.send(msg)

        else:
            self.log().warn("probe: protocol '%s' not found", name)

        return

    def send_job(self, name, pipeline, image, timestamp, deadline):
        """Sends jobs to devices."""

        protocol = self.protocols.get(name)
        if protocol:
            job = Job(self.next_job_id(), pipeline, image)
            job.start = timestamp
            job.deadline = deadline

            msg = Message(self.name, Message.TYPE_JOB, job)

            self.log().info("sending job %d to '%s'", job.job_id, name)
            self.log().debug('%s', job)
            protocol.send(msg)

        else:
            self.log().warn("send_job: protocol '%s' not found", name)

        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'dispatcher_output.log'

    logging.config.dictConfig(mylogcfg)

    Dispatcher().start()
