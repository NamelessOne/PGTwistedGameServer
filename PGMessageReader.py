from struct import *


class MessageReader:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def readByte(self):
        retval = unpack('!B', self.data[self.offset:self.offset + 1])[0]
        self.offset += 1
        return retval

    def readInt(self):
        retval = unpack('!I', self.data[self.offset:self.offset + 4])[0]
        self.offset += 4
        return retval

    def readString(self):
        strLength = self.readInt()
        unpackStr = '!%ds' % strLength
        retval = unpack(unpackStr, self.data[self.offset:self.offset + strLength])[0]
        self.offset = self.offset + strLength
        return retval

    def readByteArray(self):
        arrayLength = self.readInt()
        #b = bytearray()
        b = []
        for i in range(0, arrayLength):
            b.append(self.readByte())
        self.offset += arrayLength
        return b
