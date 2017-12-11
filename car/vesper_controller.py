import Queue
import thread
import threading
import time
import traceback

import sys
sys.path.append('../')

import config as cfg

from common import AvgItem
from common import Controller
from common import bounded
from dispatcher import Dispatcher


class VesperController(Controller):
    VAL_AVG_FPS = 'FPS.avg'
    VAL_FRAME_RATE = 'Frame Rate'
    VAL_T_0 = 'T_o'
    VAL_M_0 = 'M_o'
    VAL_PIPELINE = '~pipeline'

    QUEUE_TIMEOUT = 1.0

    def __init__(self):
        Controller.__init__(self)
        self.running = threading.Event()

        self.avg_fps = AvgItem(cfg.EWMA_ALPHA)
        self.metrics = {}

        self.values = {}
        self.values[self.VAL_T_0] = cfg.T_o
        self.values[self.VAL_M_0] = cfg.M_o
        self.values[self.VAL_AVG_FPS] = 0.0
        self.values[self.VAL_PIPELINE] = 0

        self.connected = set()
        self.values['connected'] = self.connected

        self.processors = set()

        self.constraint_lock = threading.Lock()
        return

    def throughput_constraint(self):
        """Returns throughput constraint."""
        with self.constraint_lock:
            return self.values[self.VAL_T_0]

    def makespan_constraint(self):
        """Returns makespan constraint."""
        with self.constraint_lock:
            return self.values[self.VAL_M_0]

    def start(self):
        """Starts controller thread."""
        self.running.set()
        Controller.start(self)
        return

    def stop(self):
        """Stops controller thread."""
        self.log().info('stopping controller')
        self.running.clear()
        return

    def estimated_makespan(self, name, pipeline):
        """Calculates a device's estimate makespan for specified pipeline."""
        try:
            node = self.dispatcher.nodes[name]
        except KeyError:
            self.log().warn("estimated_makespan: node '%s' not found", name)
            return sys.maxint

        with node.lock:
            try:
                makespan = cfg.PIPELINES[pipeline][1][name[:3]] / node.processing_rate.get()
            except ZeroDivisionError:
                return sys.maxint

            makespan += node.rtt.get()

        return makespan

    def device_usable(self, name):
        """Returns if device can satisfy makespan constraint."""
        est_makespan = self.estimated_makespan(name, self.get_pipeline())
        self.log().debug("estimated makespan %0.6f for '%s' (constraint: %0.3f)",
                         est_makespan, name, self.makespan_constraint())

        if est_makespan <= self.makespan_constraint():
            return True
        else:
            return False

    def run(self):
        """Controller thread target."""
        self.log().info('running controller')

        try:
            while self.running.is_set():
                try:
                    name = self.dispatcher.tokens.get(True, self.QUEUE_TIMEOUT)
                except Queue.Empty:
                    continue

                self.log().debug("got '%s' token", name)

                # Check if device is usable, otherwise probe
                if not self.device_usable(name):
                    # Schedule probe
                    self.dispatcher.probe(name, self.get_pipeline())
                    continue

                while self.running.is_set():
                    try:
                        timestamp, image = self.dispatcher.imagebuf.get(True, self.QUEUE_TIMEOUT)
                    except Queue.Empty:
                        continue

                    now = time.time()
                    elapsed = now - timestamp

                    self.log().debug('got image timestamp: %0.6f, elapsed: %0.6f',
                                     timestamp, elapsed)

                    if elapsed > self.makespan_constraint():
                        # Image has expired
                        self.log().debug('image expired (%0.6f seconds old)',
                                         elapsed)
                        continue

                    # Schedule job
                    deadline = now + self.makespan_constraint()
                    self.dispatcher.send_job(name, self.get_pipeline(), image, timestamp, deadline)

                    break   # Get next token

        except:
            self.log().error(traceback.format_exc())
            thread.interrupt_main()

        self.log().info('controller finished')
        return

    def loop(self):
        """Controller action loop."""
        self.log().info('controller loop')

        if cfg.CAMERA_NAME in self.connected:
            # Adjust frame rate
            try:
                avg_fps = self.values[self.VAL_AVG_FPS]
                t0 = self.throughput_constraint()
                ratio = float(t0)/avg_fps

                rate = bounded(t0*ratio, t0, 1.2 * t0)

            except ZeroDivisionError:
                rate = t0

            self.set_frame_rate(rate)

        # Check pipeline options
        pipeline = 0
        for i in xrange(0, len(cfg.PIPELINES)):
            self.log().debug('considering pipeline %d', i)
            throughput = 0.0

            for name in self.processors:
                est_makespan = self.estimated_makespan(name, i)
                if est_makespan < self.makespan_constraint():
                    partial = 1/est_makespan
                    throughput += partial
                    self.log().debug("'%s' has estimated makespan %0.3f", name,
                                    est_makespan)
                    self.log().debug("'%s' can contribute %0.3f", name, partial)

                else:
                    self.log().debug("'%s' too slow with estimated makespan %0.3f",
                                     name, est_makespan)

            self.log().debug('throughput estimate for pipeline %d: %0.3f fps (constraint: %0.3f)',
                             i, throughput, self.throughput_constraint())

            if throughput >= self.throughput_constraint()+1:
                pipeline = i
            else:
                # Higher pipelines will be slower, so can stop here
                break

        if self.dispatcher.imagebuf.qsize() > 30:
            # Make sure image buffer doesn't grow out of control
            self.log().warn('clearing imagebuf')
            self.dispatcher.imagebuf = Queue.Queue()

        self.set_pipeline(pipeline)
        return

    def logon(self, name):
        """Handles device logon."""
        Controller.logon(self, name)
        self.connected.add(name)

        if name == cfg.CAMERA_NAME:
            self.set_frame_rate(self.throughput_constraint())
        else:
            self.processors.add(name)

        return

    def logoff(self, name):
        """Handles device logoff."""
        Controller.logoff(self, name)
        self.processors.discard(name)
        self.connected.discard(name)
        return

    def put_metrics(self, metrics):
        """Process system metrics."""
        self.metrics = metrics

        if Dispatcher.ITEM_FPS in metrics:
            fps = metrics[Dispatcher.ITEM_FPS]
            self.avg_fps.add(fps)
            self.values[self.VAL_AVG_FPS] = self.avg_fps.pull()

        self.log().debug('values: %s', self.values)
        return

    def get_values(self):
        """Retrieves controller's data."""
        return self.values

    def set_frame_rate(self, rate):
        """Sets frame rate."""
        params = [
            ('frame_rate', rate),
            ('camera', True)
        ]
        self.send_params(cfg.CAMERA_NAME, params)

        self.values[self.VAL_FRAME_RATE] = rate
        return

    def set_constraints(self, throughput, makespan):
        """Sets throughput and makespan constraints."""
        with self.constraint_lock:
            self.values[self.VAL_T_0] = throughput
            self.values[self.VAL_M_0] = makespan

        return

    def get_pipeline(self):
        """Returns active pipeline."""
        return self.values[self.VAL_PIPELINE]

    def set_pipeline(self, pipeline):
        """Sets the active pipeline."""
        self.values[self.VAL_PIPELINE] = pipeline
        self.log().info('selected pipeline %d', pipeline)
        return
