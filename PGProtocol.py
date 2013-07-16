from struct import *

from twisted.internet.protocol import Protocol

from PGMessageReader import *
from PGMessageWriter import *


TO_SERVER_MESSAGE_PLAYER_CONNECTED = 0
TO_SERVER_MESSAGE_PROVIDE_PICTURE = 12

TO_CLIENT_MESSAGE_NOT_IN_MATCH = 1
TO_CLIENT_MESSAGE_PLAYERS_ROLE = 9
TO_CLIENT_MESSAGE_OPPONENT_LOGIN = 10
TO_CLIENT_MESSAGE_PROVIDE_PICTURE = 11

MESSAGE_START_MATCH = 2
MESSAGE_MATCH_STARTED = 3
MESSAGE_PLAYER_MOVED = 5
MESSAGE_GAME_OVER = 6
MESSAGE_RESTART_MATCH = 7
MESSAGE_NOTIFY_READY = 8


class PaintingGameProtocol(Protocol):
    def __init__(self):
        self.inBuffer = ""
        self.player = None

    def log(self, message):
        if self.player:
            print("%s: %s" % (self.player.login, message))
        else:
            print("%s: %s" % (self, message))

    def connectionMade(self):
        self.log("Connection made")

    def connectionLost(self, reason):
        self.log("Connection lost: %s" % str(reason))
        self.factory.connectionLost(self)

    def sendMessage(self, message):
        msgLen = pack('!I', len(message.data))
        self.transport.write(msgLen)
        self.transport.write(message.data)

    def sendNotInMatch(self):
        message = MessageWriter()
        message.writeByte(TO_CLIENT_MESSAGE_NOT_IN_MATCH)
        self.log("Sent MESSAGE_NOT_IN_MATCH")
        self.sendMessage(message)

    def playerConnected(self, message):
        playerId = message.readString()
        login = message.readString()
        continueMatch = message.readByte()
        self.log("Recv MESSAGE_PLAYER_CONNECTED %s %s %d" % (playerId, login, continueMatch))
        self.factory.playerConnected(self, playerId, login, continueMatch)

    def processMessage(self, message):
        messageId = message.readByte()
        if messageId == MESSAGE_NOTIFY_READY:
            return self.notifyReady(message)
        if messageId == TO_SERVER_MESSAGE_PLAYER_CONNECTED:
            return self.playerConnected(message)
        if messageId == MESSAGE_START_MATCH:
            return self.startMatch(message)
        if messageId == MESSAGE_RESTART_MATCH:
            return self.restartMatch(message)
        if messageId == TO_SERVER_MESSAGE_PROVIDE_PICTURE:
            return self.pictureToServer(message)
        self.log("Unexpected message: %d" % messageId)

    def dataReceived(self, data):
        #Get message
        self.inBuffer = self.inBuffer + data
        while True:
            if len(self.inBuffer) < 4:
                return
            msgLen = unpack('!I', self.inBuffer[:4])[0]
            if len(self.inBuffer) < msgLen:
                return
            messageString = self.inBuffer[4:msgLen + 4]
            self.inBuffer = self.inBuffer[msgLen + 4:]
            message = MessageReader(messageString)
            self.processMessage(message)

    def sendMatchStarted(self, match):
        message = MessageWriter()
        message.writeByte(MESSAGE_MATCH_STARTED)
        match.write(message)
        self.log("Sent MATCH_STARTED %s" % (str(match)))
        self.sendMessage(message)

    def startMatch(self, message):
        numPlayers = message.readByte()
        playerIds = []
        for i in range(0, numPlayers):
            playerId = message.readString()
            playerIds.append(playerId)
        self.log("Recv MESSAGE_START_MATCH %s" % (str(playerIds)))
        self.factory.startMatch(playerIds)

    def sendPlayerMoved(self, playerIndex, posX):
        message = MessageWriter()
        message.writeByte(MESSAGE_PLAYER_MOVED)
        message.writeByte(playerIndex)
        message.writeInt(posX)
        self.log("Sent PLAYER_MOVED %d %d" % (playerIndex, posX))
        self.sendMessage(message)

    def sendGameOver(self, winnerIndex):
        message = MessageWriter()
        message.writeByte(MESSAGE_GAME_OVER)
        message.writeByte(winnerIndex)
        self.log("Sent MESSAGE_GAME_OVER %d" % winnerIndex)
        self.sendMessage(message)

    def movedSelf(self, message):
        posX = message.readInt()
        self.log("Recv MESSAGE_MOVED_SELF %d" % posX)
        self.player.match.movedSelf(posX, self.player)
        return self.movedSelf(message)

    def pictureToServer(self, message):
        self.log("Recv PICTURE")
        b = message.readByteArray()
        self.player.match.sendPictureFromPlayer(self.player, b)
        #TODO

    def sendPicture(self, b):
        self.log("Send PICTURE")
        message = MessageWriter()
        message.writeByte(TO_CLIENT_MESSAGE_PROVIDE_PICTURE)
        message.writeByteArray(b)
        self.sendMessage(message)

    def restartMatch(self, message):
        self.log("Recv MESSAGE_RESTART_MATCH")
        self.player.match.restartMatch(self.player)

    def sendNotifyReady(self, playerId):
        message = MessageWriter()
        message.writeByte(MESSAGE_NOTIFY_READY)
        message.writeString(playerId)
        self.log("Sent PLAYER_NOTIFY_READY %s" % playerId)
        self.sendMessage(message)

    def notifyReady(self, message):
        inviter = message.readString()
        self.log("Recv MESSAGE_NOTIFY_READY %s" % inviter)
        self.factory.notifyReady(self.player, inviter)

    def setRole(self, role):
        self.player.role = role
        message = MessageWriter()
        message.writeByte(TO_CLIENT_MESSAGE_PLAYERS_ROLE)
        message.writeByte(role)
        self.log("Sent MESSAGE_SET_ROLE %s %d" % (self.player.login, role))
        self.sendMessage(message)

    def sendOpponentLogin(self, login):
        message = MessageWriter()
        message.writeByte(TO_CLIENT_MESSAGE_OPPONENT_LOGIN)
        message.writeString(login)
        self.log("Sent MESSAGE_SEND_OPPONENT_LOGIN %s %s" % (self.player.login, login))
        self.sendMessage(message)