import logging

class MyObject(object):
    def log(self):
        return logging.getLogger(self.__class__.__name__)
