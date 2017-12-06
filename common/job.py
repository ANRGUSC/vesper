import time

from myobject import MyObject

class Job(MyObject):

    def __init__(self, job_id, pipeline, data, probe=False):
        self.job_id = job_id
        self.pipeline = pipeline
        self.data = data
        self.probe = probe

        self.deadline = 0.0

        # End-to-end time (dispatcher)
        self.start = time.time()
        self.end = 0.0

        # Processing time (device)
        self.arrived = 0.0
        self.left = 0.0
        return

    def __repr__(self):
        s = '<Job %d: P%d ' % (self.job_id, self.pipeline)

        if self.probe:
            s += 'Probe '

        s += '(%d bytes),' % (len(self.data))

        # Include times if set
        if self.deadline:
            s += ' deadline: %0.3f' % self.deadline
        if self.start:
            s += ' start: %0.3f' % self.start
        if self.end:
            s += ', end: %0.3f' % self.end
        if self.arrived:
            s += ', arrived: %0.3f' % self.arrived
        if self.left:
            s += ', left: %0.3f' % self.left

        s += '>'
        return s


if __name__ == '__main__':
    j = Job(10, 1, ' ' * 100)
    print j

    j.probe = True
    print j

    j.arrived = time.time()
    print j

    j.left = time.time()
    j.end = time.time()
    print j
