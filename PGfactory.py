from twisted.internet.protocol import Factory
from collections import deque
import random

from PGPlayer import *
from PGProtocol import *
from PGMatch import *


class PaintingGameFactory(Factory):
    def __init__(self):
        self.protocol = PaintingGameProtocol
        self.players2 = deque()

    def connectionLost(self, protocol):
        for existingPlayer in self.players2:
            if existingPlayer.protocol == protocol:
                existingPlayer.protocol = None

    def playerConnected(self, protocol, playerId, alias, continueMatch):
        for existingPlayer in self.players2:
            if existingPlayer.playerId == playerId:
                existingPlayer.protocol = protocol
                protocol.player = existingPlayer
                if existingPlayer.match:
                    print("TODO: Already in match case")
                    if continueMatch:
                        existingPlayer.protocol.sendMatchStarted(existingPlayer.match)
                    else:
                        print "Quitting match!"
                        existingPlayer.match.quit()
                else:
                    existingPlayer.protocol.sendNotInMatch()
                return
        newPlayer = PaintingGamePlayer(protocol, playerId, alias)
        protocol.player = newPlayer
        newPlayer.protocol.sendNotInMatch()
        #TODO
        self.findOpponent(newPlayer)

    def startMatch(self, playerIds):
        matchPlayers = []
        for existingPlayer in self.players:
            if existingPlayer.playerId in playerIds:
                if existingPlayer.match is not None:
                    return
                matchPlayers.append(existingPlayer)
        match = PaintingGameMatch(matchPlayers)
        for matchPlayer in matchPlayers:
            matchPlayer.match = match
            matchPlayer.protocol.sendMatchStarted(match)

    def notifyReady(self, player, inviter):
        for existingPlayer in self.players2:
            if existingPlayer.playerId == inviter:
                existingPlayer.protocol.sendNotifyReady(player.playerId)

    def findOpponent(self, player):
        try:
            opponent = self.players2.popleft()
        except IndexError:
            self.players2.append(player)
        else:
            print("Match between %s and %s" % (opponent.login, player.login))
            players3 = deque()
            players3.append(player)
            players3.append(opponent)
            items = [1, 0]
            random.shuffle(items)
            player.role = items[0]
            opponent.role = items[1]
            player.protocol.setRole(player.role)
            opponent.protocol.setRole(opponent.role)
            player.protocol.sendOpponentLogin(opponent.login)
            opponent.protocol.sendOpponentLogin(player.login)
            game = PaintingGameMatch(players3)
            player.match = game
            opponent.match = game