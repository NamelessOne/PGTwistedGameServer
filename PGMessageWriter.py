from struct import *


class MessageWriter:
    def __init__(self):
        self.data = ""

    def writeByte(self, value):
        self.data += pack('!B', value)

    def writeInt(self, value):
        self.data += pack('!I', value)

    def writeString(self, value):
        self.writeInt(len(value))
        packStr = '!%ds' % (len(value))
        self.data += pack(packStr, value)

    def writeByteArray(self, bs):
        self.writeInt(len(bs))
        for b in bs:
            self.writeByte(b)