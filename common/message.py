from myobject import MyObject

class Message(MyObject):
    TYPE_LOGIN  = 'LOGIN'
    TYPE_JOB    = 'JOB'
    TYPE_RESULT = 'RESULT'
    TYPE_PARAMS = 'PARAMS'
    TYPE_IMAGE  = 'IMAGE'

    def __init__(self, name, msg_type, data=None):
        self.name = name
        self.type = msg_type
        self.data = data

    def __str__(self):
        return "<Message '%s': '%s'>" % (self.name, self.type)

    def __repr__(self):
        return "<Message '%s': '%s' [%s]>" % \
                (self.name, self.type, self.data)

