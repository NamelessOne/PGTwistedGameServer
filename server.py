from twisted.internet import reactor
from PGfactory import *

factory = PaintingGameFactory()
reactor.listenTCP(1955, factory)
print("Painting Game server started")
reactor.run()