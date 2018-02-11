
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


class Shoe:

    shuffle_specs = [[95, 8],
		     [92, 7],
		     [89, 6],
		     [86, 5],
		     [84, 4],
		     [82, 3],
		     [81, 2],
		     [80, 1]]

    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.cards = []

    def need_to_shuffle(self):
        if len(self.cards) == 0:
            return True

        total_cards = self.num_decks * 52
        cards_dealt = total_cards - len(self.cards)
        used = (cards_dealt / total_cards) * 100.0

        for x in range(len(Shoe.shuffle_specs)):
            if used > Shoe.shuffle_specs[x][0] and self.num_decks == Shoe.shuffle_specs[x][1]:
                return True

        return False

    def shuffle(self):
        from random import shuffle as sh
        self.new_regular()
        sh(self.cards)

    def get_next_card(self):
        return self.cards.pop(0)

    def new_regular(self):
        self.cards = []
        for decks in range(self.num_decks):
            for suite in range(4):
                for value in range(13):
                    self.cards.append(Card(value, suite))


class Card:

    faces = [["🂡", "🂱", "🃁", "🃑"],
	     ["🂢", "🂲", "🃂", "🃒"],
	     ["🂣", "🂳", "🃃", "🃓"],
	     ["🂤", "🂴", "🃄", "🃔"],
	     ["🂥", "🂵", "🃅", "🃕"],
	     ["🂦", "🂶", "🃆", "🃖"],
	     ["🂧", "🂷", "🃇", "🃗"],
	     ["🂨", "🂸", "🃈", "🃘"],
	     ["🂩", "🂹", "🃉", "🃙"],
	     ["🂪", "🂺", "🃊", "🃚"],
	     ["🂫", "🂻", "🃋", "🃛"],
	     ["🂭", "🂽", "🃍", "🃝"],
	     ["🂮", "🂾", "🃎", "🃞"],
	     ["🂠", "",  "",  "" ]]

    def __init__(self, value, suite):
        self.value = value
        self.suite = suite

    def __str__(self):
        return u'%s' % Card.faces[self.value][self.suite]

    def is_ace(self):
        return self.value == 0

    def is_ten(self):
        return self.value > 8
