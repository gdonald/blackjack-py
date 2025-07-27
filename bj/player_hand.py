
import sys

from enum import Enum
from bj.hand import Hand, CountMethod

class HandStatus(Enum):
    Unknown = 0
    Won = 1
    Lost = 2
    Push = 3

class PlayerHand(Hand):

    max_player_hands = 7

    def __init__(self, game, bet):
        super().__init__(game)
        self.bet = bet
        self.status = HandStatus.Unknown
        self.paid = False

    def is_busted(self):
        return self.get_value(CountMethod.Soft) > 21

    def get_value(self, count_method):
        total = 0
        for x in range(len(self.cards)):
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
            if not self.paid:
                if self.is_busted():
                    self.paid = True
                    self.status = HandStatus.Lost
                    self.game.money -= self.bet
            return True
        return False

    def can_split(self):
        if self.stood or len(self.game.player_hands) >= PlayerHand.max_player_hands:
            return False
        if self.game.money < self.game.all_bets() + self.bet:
            return False
        if len(self.cards) == 2 and self.cards[0].value == self.cards[1].value:
            return True
        return False

    def can_dbl(self):
        if self.game.money < self.game.all_bets() + self.bet:
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
        self.stood = True
        self.played = True
        if self.game.more_hands_to_play():
            self.game.play_more_hands()
            return
        self.game.play_dealer_hand()
        self.game.draw_hands()
        self.game.bet_options()

    def process(self):
        if self.game.more_hands_to_play():
            self.game.play_more_hands()
            return
        self.game.play_dealer_hand()
        self.game.draw_hands()
        self.game.bet_options()

    def __str__(self):
        out = ' '
        for i in range(len(self.cards)):
            c = self.cards[i]
            out = '%s%s ' % (out, self.game.card_face(c.value, c.suit))
        out = '%s ⇒  %s ' % (out, self.get_value(CountMethod.Soft))
        if self.status == HandStatus.Lost:
            out = '%s-' % out
        elif self.status == HandStatus.Won:
            out = '%s+' % out
        out = '%s$%.2f' % (out, self.bet / 100.0)
        if not self.played and self == self.game.player_hands[self.game.current_player_hand]:
            out = '%s ⇐' % out
        out = '%s ' % out
        if self.status == HandStatus.Lost:
            out = '%s%s' % (out, 'Busted!' if self.is_busted() else 'Lose!')
        elif self.status == HandStatus.Won:
            out = '%s%s' % (out, 'Blackjack!' if self.is_blackjack() else 'Win!')
        elif self.status == HandStatus.Push:
            out = '%s%s' % (out, 'Push!')
        out = '%s\n' % out
        return u'%s' % out

    def get_action(self):
        out = ' '
        if self.can_hit():
            out = '%s(H) Hit  ' % out
        if self.can_stand():
            out = '%s(S) Stand  ' % out
        if self.can_split():
            out = '%s(P) Split  ' % out
        if self.can_dbl():
            out = '%s(D) Double  ' % out
        print(u'%s' % out)
        br = False

        while True:
            c = sys.stdin.read(1)
            if c == 'h':
                br = True
                self.hit()
            elif c == 's':
                br = True
                self.stand()
            elif c == 'p':
                if self.can_split():
                    br = True
                    self.game.split_current_hand()
            elif c == 'd':
                br = True
                self.dbl()
            if br:
                break
