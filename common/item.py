import threading
import time

from myobject import MyObject


class Item(MyObject):
    """Item base class."""

    def __init__(self):
        self.lock = threading.RLock()
        return

    def reset(self):
        """Resets item value"""
        raise NotImplementedError

    def add(self, amount):
        """Adjusts item value."""
        raise NotImplementedError

    def get(self):
        """Gets item value (without changing)."""
        raise NotImplementedError

    def pull(self):
        """Gets and resets item value."""
        with self.lock:
            value = self.get()
            self.reset()
            return value


class RateItem(Item):
    """Item for rate measurement."""

    def __init__(self):
        Item.__init__(self)
        self.reset()
        return

    def reset(self):
        with self.lock:
            self.value = 0
            self.start = time.time()

        return

    def add(self, amount=1):
        with self.lock:
            self.value += amount

        return

    def get(self):
        with self.lock:
            now = time.time()
            return self.value / (now - self.start)


class AvgItem(Item):
    """Item for average measurement."""

    def __init__(self, param=1.0):
        Item.__init__(self)
        self.param = param

        self.init = False
        self.previous = 0.0

        self.reset()
        return

    def reset(self):
        with self.lock:
            self.value = 0.0
            self.count = 0

        return

    def add(self, amount):
        with self.lock:
            self.value += amount
            self.count += 1

        return

    def get(self):
        with self.lock:
            if self.count:
                avg = float(self.value) / self.count
            else:
                avg = 0.0

            if self.init:
                value = (avg * self.param) + (self.previous * (1 - self.param))
            else:
                value = avg
                self.init = True

            self.previous = value

        return value
