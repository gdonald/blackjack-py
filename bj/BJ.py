
class Card:

    def __init__(self, value, suite):
        self.value = value
        self.suite = suite

    def __str__(self):
        return u'%s %s' % (self.suite, self.value)


class Shoe:

    def __init__(self):
        pass


class Hand:

    def __init__(self):
        pass


class DealerHand(Hand):

    def __init__(self):
        pass


class PlayerHand(Hand):

    def __init__(self):
        pass


class Game():

    def __init__(self):
        pass

