import threading
import time

from item import RateItem, AvgItem
from myobject import MyObject


class Monitor(MyObject, threading.Thread):
    """Tracks performance data."""

    ITEM_RATE   = 'rate'
    ITEM_AVG    = 'avg'

    def __init__(self, callback=None, period=1.0):
        threading.Thread.__init__(self, name='Monitor')

        self.callback = callback
        self.period = period

        self.running = threading.Event()

        self.register = {}
        self.values = {}

        self.lock = threading.Lock()

        self.log().debug('period: %s', self.period)
        return

    def start(self):
        """Starts monitor."""
        self.log().info('starting monitor')
        self.running.set()

        threading.Thread.start(self)
        return

    def stop(self):
        """Stops monitor."""
        self.log().info('stopping monitor')
        self.running.clear()
        return

    def run(self):
        """Monitoring loop."""
        while self.running.is_set():
            time.sleep(self.period)

            # Update values
            with self.lock:
                for key, item in self.register.iteritems():
                   self.values[key] = item.pull()

            # Callback
            if self.callback:
                t = threading.Thread(name='Monitor.callback', target=self.callback,
                                     args=(self.values.copy(),))
                t.start()

        self.log().info('monitor finished')
        return

    def register_item(self, name, item_type, param=None):
        """Registers a new item for monitoring."""
        self.log().debug("registering '%s' with type: %s (%s)",
                         name, item_type, param)

        if name in self.register:
            self.log().warn("'%s' already registered", name)
            return

        if item_type == self.ITEM_RATE:
            item = RateItem()

        elif item_type == self.ITEM_AVG:
            if param:
                item = AvgItem(param)
            else:
                item = AvgItem()

        else:
            self.log().warning('unknown item type: %s', item_type)

        with self.lock:
            self.register[name] = item
            self.values[name] = 0.0

        return

    def remove_item(self, name):
        """Removes a monitored item."""
        if not name in self.register:
            self.log().warn("could not remove '%s': item not found", name)

        with self.lock:
            del self.register[name]
            del self.values[name]

        return


    def update_item(self, name, amount):
        """Updates the value of a monitored item."""
        if not name in self.register:
            self.log().warn("could not update '%s': item not found", name)

        with self.lock:
            item = self.register[name]
            item.add(amount)

        return


if __name__ == '__main__':
    import logging.config

    import sys
    sys.path.append('../')

    import config as cfg

    mylogcfg = cfg.LOGCFG
    mylogcfg['handlers']['file']['filename'] = '/dev/null'

    logging.config.dictConfig(mylogcfg)

    count = 0
    def my_callback(values):
        global count

        print values
        count += 1

        if count == 2:
            m.stop()

    m = Monitor(my_callback)
    m.register_item('test_rate', Monitor.ITEM_RATE)
    m.register_item('test_avg', Monitor.ITEM_AVG, 0.5)

    m.update_item('test_rate', 5)
    m.update_item('test_avg', 6)
    m.update_item('test_avg', 10)

    m.start()
