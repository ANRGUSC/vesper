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
