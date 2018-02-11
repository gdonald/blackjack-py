
from enum import Enum

class HandStatus(Enum):
    Unknown = 0
    Won = 1
    Lost = 2
    Push = 3


class CountMethod(Enum):
    Soft = 0
    Hard = 1


class Game():

    def __init__(self):
        pass


class Hand:

    def __init__(self, game):
        self.game = game
        self.cards = []
        self.stood = False
        self.played = False

    def deal_card(self):
        self.cards.append(self.game.shoe.get_next_card())

    def is_blackjack(self):
        if len(self.card) != 2:
            return False
        if self.cards[0].is_ace() and self.cards[1].is_ten():
            return True
        if self.cards[1].is_ace() and self.cards[0].is_ten():
            return True
        return False


class PlayerHand(Hand):

    max_player_hands = 7

    def __init__(self, game, bet):
        super().__init__(game)
        self.bet = bet
        self.status = HandStatus.Unknown
        self.payed = False

    def is_busted(self):
        return self.get_value(CountMethod.Soft) > 21

    def get_value(self, count_method):
        v = 0
        total = 0
        for x in range(len(self.cards.size)):
            tmp_v = self.cards[x].value + 1
            v = 10 if tmp_v > 9 else tmp_v
            if count_method == CountMethod.Soft and v == 1 and total < 11:
                v = 11
            total += v
        if count_method == CountMethod.Soft and total > 21:
            return self.get_value(CountMethod.Hard)
        return total

    def is_done(self):
        if self.played or self.stood or self.is_blackjack() or self.is_busted() or 21 == self.get_value(CountMethod.Soft) or 21 == self.get_value(CountMethod.Hard):
            self.played = True
            if not self.payed:
                if self.is_busted():
                    self.payed = True
                    self.status = HandStatus.Lost
                    self.game.money -= self.bet
            return True
        return False

    def can_split(self):
        if self.stood or len(self.hands) >= PlayerHand.max_player_hands:
            return False
        if self.game.money < self.game.all_bets() + self.bet:
            return False
        if len(self.cards) == 2 and self.cards[0].value == self.cards[1].value:
            return True
        return False

    def can_dbl(self):
        if self.game.money < self.game.all_bets() + bet:
            return False
        if self.stood or len(self.cards) != 2 or self.is_busted() or self.is_blackjack():
            return False
        return True

    def can_stand(self):
        if self.stood or self.is_busted() or self.is_blackjack():
            return False
        return True

    def can_hit(self):
        if self.played or self.stood or 21 == self.get_value(CountMethod.Hard) or self.is_blackjack() or self.is_busted():
            return False
        return True

    def hit(self):
        self.deal_card()
        if self.is_done():
            self.process()
            return
        self.game.draw_hands()
        self.game.player_hands[self.game.current_player_hand].get_action()

    def dbl(self):
        self.deal_card()
        self.played = True
        self.bet *= 2
        if self.is_done():
            self.process()

    def stand(self):
        self.stoof = True
        self.played = True
        if self.game.more_hands_to_play():
            self.game.play_more_hands()
            return
        self.game.play_dealer_hand()
        self.game.draw_hands()
        self.game.draw_player_bet_options()

    def process(self):
        if self.game.more_hands_to_play():
            self.game.play_more_hands()
            return
        self.game.play_dealer_hand()
        self.game.draw_hands()
        self.game.draw_player_bet_options()

    def __str__(self, index):
        out = ' '
        for i in range(len(self.cards)):
            out.append('%s ' % self.cards[i])
        out.append(' ⇒  %s ' % self.get_value(CountMethod.Soft))
        if self.status == HandStatus.Lost:
            out.append('-')
        elif self.status == HandStatus.Won:
            out.append('+')
        out.append('$%s' % self.bet / 100.0)
        if not self.played and index == self.game.current_player_hand:
            out.append(' ⇐')
        out.append(' ')
        if self.status == HandStatus.Lost:
            out.append('Busted!' if self.is_busted() else 'Lose!')
        elif self.status == HandStatus.Won:
            out.append('Blackjack!' if self.is_blackjack() else 'Win!')
        elif self.status == HandStatus.Push:
            out.append('Push!')
        out.append('\n\n')
        return u'%s' % out

    def get_action(self):
        out = ' '
        if self.can_hit():
            out.append('(H) Hit  ')
        if self.can_stand():
            out.append('(S) Stand  ')
        if self.can_split():
            out.append('(P) Split  ')
        if self.can_dbl():
            out.append('(D) Double  ')
        print(u'%s\n' % out)
        br = False
        c = ''
        while True:
            c = input()
            if c == 'h':
                br = True
                self.hit()
            elif c == 's':
                br = True
                self.stand()
            elif c == 'p':
                br = True
                self.game.split_current_hand()
            elif c == 'd':
                br = True
                self.dbl()
            if br:
                break



class DealerHand(Hand):

    def __init__(self, game):
        super().__init__(game)
        self.hide_down_card = True

    def is_busted(self):
        return self.get_value(CountMethod.Soft) > 21

    def get_value(self, count_method):
        v = 0
        total = 0
        for x in range(len(self.cards.size)):
            if x == 1 and self.hide_down_card:
                continue
            tmp_v = self.cards[x].value + 1
            v = 10 if tmp_v > 9 else tmp_v
            if count_method == CountMethod.Soft and v == 1 and total < 11:
                v = 11
            total += v
        if count_method == CountMethod.Soft and total > 21:
            return self.get_value(CountMethod.Hard)
        return total

    def __str__(self):
        out = ' '
        for i in range(len(self.cards)):
            out.append(Card.faces[13][0] if i == 1 and self.hide_down_card else Card.faces)
            out.append(' ')
        out.append(' ⇒  %s' % self.get_value(CountMethod.Soft))
        return u'%s' % out

    def upcard_is_ace(self):
        return self.cards[0].is_ace()


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
        for x in range(7):
            sh(self.cards)

    def get_next_card(self):
        return self.cards.pop(0)

    def new_regular(self):
        self.cards = []
        for _ in range(self.num_decks):
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
