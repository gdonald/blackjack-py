
from bj.card import Card

class Shoe:

    shuffle_specs = [80, 81, 82, 84, 86, 89, 92, 95]

    def __init__(self):
        self.num_decks = 8
        self.cards = []
        self.cards_per_deck = 52

    def need_to_shuffle(self):
        if len(self.cards) == 0:
            return True
        total_cards = self.num_decks * 52
        cards_dealt = total_cards - len(self.cards)
        used = (cards_dealt / total_cards) * 100.0

        return used > Shoe.shuffle_specs[self.num_decks - 1]

    def shuffle(self):
        from random import shuffle as sh
        for x in range(7):
            sh(self.cards)

    def get_next_card(self):
        return self.cards.pop(0)

    def build_new_shoe(self, deck_type):
        match deck_type:
            case 2:
                self.new_aces()
            case 3:
                self.new_jacks()
            case 4:
                self.new_aces_jacks()
            case 5:
                self.new_sevens()
            case 6:
                self.new_eights()
            case _:
                self.new_regular()
        self.shuffle()

    def get_total_cards(self):
        return self.num_decks * self.cards_per_deck

    def new_shoe(self, values):
        total_cards = self.get_total_cards()
        self.cards = []
        while len(self.cards) < total_cards:
            for _ in range(self.num_decks):
                for suit in range(4):
                    if len(self.cards) >= total_cards:
                        break
                    for value in values:
                        if len(self.cards) >= total_cards:
                            break
                        self.cards.append(Card(value, suit))

    def new_regular(self):
        self.new_shoe(list(range(0, 13)))

    def new_aces(self):
        self.new_shoe([0])

    def new_jacks(self):
        self.new_shoe([10])

    def new_aces_jacks(self):
        self.new_shoe([0, 10])

    def new_sevens(self):
        self.new_shoe([6])

    def new_eights(self):
        self.new_shoe([7])
