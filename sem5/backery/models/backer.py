import random

from helpers.names import getRandomName
import constants


class Backer:
    completedCount = 0

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name


def createNew():
    return Backer(str(random.randint(1000, 9999)),
                  getRandomName())


def newBunTimeout():
    return constants.bunTimeout
    # return 2
