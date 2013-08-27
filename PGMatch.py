from time import time

from twisted.internet.task import LoopingCall


MATCH_STATE_ACTIVE = 0
MATCH_STATE_GAME_OVER = 1
PLAYER_WIN_X = 445
SECS_FOR_SHUTDOWN = 30


class PaintingGameMatch:
    def __init__(self, players):
        self.players = players
        self.state = MATCH_STATE_ACTIVE
        self.pendingShutdown = False
        self.shutdownTime = 0
        #self.timer = LoopingCall(self.update)
        #self.timer.start(500)

    def __repr__(self):
        return "%d %s" % (self.state, str(self.players))

    def write(self, message):
        message.writeByte(self.state)
        message.writeByte(len(self.players))
        for matchPlayer in self.players:
            matchPlayer.write(message)

    def movedSelf(self, posX, player):
        if self.state == MATCH_STATE_GAME_OVER:
            return
        player.posX = posX
        if player.posX >= PLAYER_WIN_X:
            self.state = MATCH_STATE_GAME_OVER
            for matchPlayer in self.players:
                if matchPlayer.protocol:
                    matchPlayer.protocol.sendGameOver(player.match.players.index(player))
        for i in range(0, len(self.players)):
            matchPlayer = self.players[i]
            if matchPlayer != player:
                if matchPlayer.protocol:
                    matchPlayer.protocol.sendPlayerMoved(i, posX)

    def restartMatch(self, player):
        if self.state == MATCH_STATE_ACTIVE:
            return
        self.state = MATCH_STATE_ACTIVE
        for matchPlayer in self.players:
            matchPlayer.posX = 25
        for matchPlayer in self.players:
            if matchPlayer.protocol:
                matchPlayer.protocol.sendMatchStarted(self)

    def update(self):
        print "Match update: %s" % (str(self))
        if self.pendingShutdown:
            cancelShutdown = True
            for player in self.players:
                if player.protocol is None:
                    cancelShutdown = False
            if time() > self.shutdownTime:
                print "Time elapsed, shutting down match"
                self.quit()
        else:
            for player in self.players:
                if player.protocol is None:
                    print "Player %s disconnected, scheduling shutdown" % player.alias
                    self.pendingShutdown = True
                    self.shutdownTime = time() + SECS_FOR_SHUTDOWN

    def quit(self):
        self.timer.stop()
        for matchPlayer in self.players:
            matchPlayer.match = None
            if matchPlayer.protocol:
                matchPlayer.protocol.sendNotInMatch()

    def sendPictureFromPlayer(self, player, b):
        for p in self.players:
            if p != player:
                p.protocol.sendPicture(b)