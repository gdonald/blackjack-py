
from enum import Enum

class CountMethod(Enum):
    Soft = 0
    Hard = 1

class Hand:

    def __init__(self, game):
        self.game = game
        self.cards = []
        self.stood = False
        self.played = False

    def deal_card(self):
        self.cards.append(self.game.shoe.get_next_card())

    def is_blackjack(self):
        if len(self.cards) != 2:
            return False
        if self.cards[0].is_ace() and self.cards[1].is_ten():
            return True
        return self.cards[1].is_ace() and self.cards[0].is_ten()
