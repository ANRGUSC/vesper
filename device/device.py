import threading
import time

import sys
sys.path.append('../')

import config as cfg

from network import Client
from common import Message
from common import Service
from pipeline import Pipeline


class Device(Service):
    """Handles communication between a device and the dispatcher."""

    def __init__(self, name):
        Service.__init__(self, name)

        self.handlers[Message.TYPE_PARAMS] = self.handle_params
        self.handlers[Message.TYPE_JOB] = self.handle_job

        self.client = Client(self, cfg.SERVER_HOST, cfg.SERVER_PORT)
        self.protocol = None

        self.pipelines = []
        for p in cfg.PIPELINES:
            pipeline = Pipeline(p[0], self)
            pipeline.start()
            self.pipelines.append(pipeline)

        return

    def start(self):
        """Starts the device client."""
        self.client.run()
        self.stop()
        return

    def stop(self):
        """Stops the device client."""
        self.client.stop()

        for pipeline in self.pipelines:
            pipeline.stop()

        return

    def send(self, message):
        if self.protocol:
            self.protocol.send(message)

        return

    def connected(self, protocol):
        """Handles connection."""
        Service.connected(self, protocol)
        self.protocol = protocol

        self.send(Message(self.name, Message.TYPE_LOGIN))
        return

    def disconnected(self, protocol):
        """Handles disconnection."""
        Service.disconnected(self, protocol)
        self.protocol = None
        return

    def handle_params(self, protocol, message):
        """Handles param messages."""
        self.log().info("received params from '%s': %s", message.name,
                        message.data)

        params = message.data
        for p in params:
            self.configure_param(p)

        return

    def configure_param(self, param):
        """Processes a parameter."""
        self.log().debug(param)

        if param[0] == 'pipeline':
            self.pipeline = param[1]

        return

    def handle_job(self, protocol, message):
        """Handles job messages."""
        job = message.data
        job.arrived = time.time()

        self.log().info('received %s', job)

        self.pipelines[job.pipeline].queue.put(job)

        #t = threading.Thread(name='worker', target=self.work, args=(job,))
        #t.start()
        return

    #def work(self, job):
    #    """For testing: performs a job."""
    #    time.sleep(cfg.PIPELINES[job.pipeline][1])
    #    job.data = ' ' * 1000
    #    self.send_result(job)
    #    return

    def send_result(self, job):
        """Sends job result to dispatcher."""
        job.left = time.time()

        if job.probe:
            prefix = 'probe '
        else:
            prefix = ''

        self.log().info('%sjob %d took %0.6f seconds', prefix, job.job_id, job.left - job.arrived)
        self.send(Message(self.name, Message.TYPE_RESULT, job))
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = '/dev/null'

    logging.config.dictConfig(mylogcfg)

    Device('device').start()
