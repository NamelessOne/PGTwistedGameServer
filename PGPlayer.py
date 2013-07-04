class PaintingGamePlayer:
    def __init__(self, protocol, playerId, login):
        self.protocol = protocol
        self.playerId = playerId
        self.login = login
        self.match = None
        self.posX = 25
        self.role = None

    def __repr__(self):
        return "%s:%d" % (self.login, self.posX)

    def write(self, message):
        message.writeString(self.playerId)
        message.writeString(self.login)
        message.writeInt(self.posX)

