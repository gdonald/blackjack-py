
import os
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

    save_file = 'bj.txt'
    min_bet = 500
    max_bet = 10000000
    
    def __init__(self):
        self.num_decks = 1
        self.money = 10000
        self.current_bet = 500
        self.load_game()
        self.shoe = Shoe(self.num_decks)
        self.dealer_hand = None
        self.current_player_hand = 0
        self.player_hands = []

    def all_bets(self):
        bets = 0
        for x in range(len(self.player_hands)):
            bets += self.player_hands[x].bet
        return bets

    def ask_insurance(self):
        out = ' Insurance?  (Y) Yes  (N) No\n'
        br = False
        c = ''
        while True:
            c = input()
            if c == 'y':
                br = True
                self.insure_hand()
            elif c == 'n':
                br = True
                self.no_insurance()
            if br:
                break

    def clear(self):
        os.system('export TERM=linux; clear')

    def deal_new_hand(self):
        if self.shoe.need_to_shuffle():
            self.shoe.shuffle()
        self.player_hands = [PlayerHand(self, self.current_bet)]
        self.current_player_hand = 0
        self.dealer_hand = DealerHand(self)
        for x in range(2):
            self.player_hands[0].deal_card()
            self.dealer_hand.deal_card()
        if self.dealer_hand.upcard_is_ace():
            self.draw_hands()
            self.ask_insurance()
            return
        if self.player_hands[0].is_done():
            self.dealer_hand.hide_down_card = False
        if self.player_hands[0].is_done():
            self.pay_hands()
            self.draw_hands()
            self.draw_player_bet_options()
            return
        self.draw_hands()
        self.player_hands[0].get_action()
        self.save_game()

    def draw_hands(self):
        self.clear()
        out = '\n Dealer:\n%s\n' % str(self.dealer_hand)
        out = '%s\n Player $%s:\n' % (out, self.money / 100.0)
        for i in range(len(self.player_hands)):
            out = '%s%s' % (out, str(self.player_hands[i]))
        print(u'%s' % out)

    def draw_player_bet_options(self):
        out = ' (D) Deal Hand  (B) Change Bet  (Q) Quit\n'
        br = False
        c = ''
        while True:
            c = input()
            if c == 'd':
                br = True
                self.deal_new_hand()
            elif c == 'b':
                br = True
                self.get_new_bet()
            elif c == 'q':
                br = True
                self.clear()
            if br:
                break

    def get_new_bet(self):
        self.clear()
        self.draw_hands()
        out = '  Current Bet: $%s  Enter New Bet: $' % self.current_bet / 100
        tmp = input()
        self.current_bet = tmp * 100
        self.normalize_bet()
        self.deal_new_hand()

    def insure_new_hand(self):
        h = self.player_hands[self.current_player_hand]
        h.bet /= 2
        h.played = True
        h.payed = True
        h.stayed = HandStatus.Lost
        self.money -= h.bet
        self.draw_hands()
        self.draw_player_bet_options()

    def more_hands_to_play(self):
        return self.current_player_hand < len(self.player_hands) - 1

    def need_to_play_dealer_hand(self):
        for x in range(len(self.player_hands)):
            h = self.player_hands[x]
            if not (h.is_busted() or h.is_busted()):
                return True
        return False

    def no_insurance(self):
        if self.dealer_hand.is_blackjack():
            self.dealer_hand.hide_down_card = False
            self.dealer_hand.played = True
            self.pay_hands()
            self.draw_hands()
            self.draw_player_bet_options()
            return
        h = self.player_hands[self.current_player_hand]
        if h.is_done():
            self.play_dealer_hand()
            self.draw_hands()
            self.draw_player_bet_options()
            return
        self.draw_hands()
        h.get_action()

    def normalize_current_bet(self):
        if self.current_bet < Game.min_bet:
            self.current_bet = Game.min_bet
        elif self.current_bet > Game.max_bet:
            self.current_bet = Game.max_bet
        if self.current_bet > self.money:
            self.current_bet = self.money

    def pay_hands(self):
        dhv = self.dealer_hand.get_value(CountMethod.Soft)
        dhb = self.dealer_hand.is_busted()
        for x in range(len(self.player_hands)):
            h = self.player_hands[x]
            if h.payed:
                continue
            h.payed = True
            phv = h.get_value(CountMethod.Soft)
            if dhb or phv > dhv:
                if h.is_blackjack():
                    h.bet *= 1.5
                self.money += h.bet
                h.status = HandStatus.Won
            elif phv < dhv:
                self.money -= h.bet
                h.status = HandStatus.Lost
            else:
                h.status = HandStatus.Push
        self.normalize_current_bet()
        self.save_game()

    def play_dealer_hand(self):
        if self.dealer_hand.is_blackjack():
            self.dealer_hand.hide_down_card = False
        if not self.need_to_play_dealer_hand():
            self.dealer_hand.played = True
            self.pay_hands()
            return
        self.dealer_hand.hide_down_card = False
        soft_count = self.dealer_hand.get_value(CountMethod.Soft)
        hard_count = self.dealer_hand.get_value(CountMethod.Hard)
        while soft_count < 18 and hard_count < 17:
            self.dealer_hand.deal_card()
            soft_count = self.dealer_hand.get_value(CountMethod.Soft)
            hard_count = self.dealer_hand.get_value(CountMethod.Hard)
        self.dealer_hand.played = True
        self.pay_hands()

    def play_more_hands(self):
        self.current_player_hand += 1
        h = self.player_hands[self.current_player_hand]
        h.deal_card()
        if h.is_done():
            h.process()
            return
        self.draw_hands()
        h.get_action()

    def run(self):
        self.deal_new_hand()
        
    def save_game(self):
        try:
            f = open(Game.save_file, 'w')
        except:
            f = None
        if f is not None:
            f.write('%s|%s|%s' % (self.num_decks, self.money, self.current_bet))
            f.close()

    def load_game(self):
        s = ''
        try:
            f = open(Game.save_file, 'r')
        except:
            f = None
        if f is not None:
            s = f.read()
            f.close()
        a = s.split('|')
        if len(a) == 3:
            self.num_decks = int(a[0])
            self.money = float(a[1])
            self.current_bet = int(a[2])
        if self.money < Game.min_bet:
            self.money = 10000
            
    def split_current_hand(self):
        current_hand = self.player_hands[self.current_player_hand]
        if not current_hand.can_split():
            self.draw_hands()
            current_hand.get_action()
            return
        self.player_hands.append(PlayerHand(self, self.current_bet))
        x = len(self.player_hands) - 1
        while x > self.current_player_hand:
            self.player_hands[x] = self.player_hands[x - 1]
            x -= 1
        this_hand = self.player_hands[self.current_player_hand]
        split_hand = self.player_hands[self.current_player_hand + 1]
        split_hand.cards = []
        c = this_hand.cards[len(this_hand.cards) - 1]
        split_hand.cards.append(c)
        this_hand.cards.pop(len(this_hand.cards) - 1)
        this_hand.deal_card()
        if this_hand.is_done():
            this_hand.process()
            return
        self.draw_hands()
        self.player_hands[self.current_player_hand].get_action()

        
class Hand:

    def __init__(self, game):
        self.game = game
        self.cards = []
        self.stood = False
        self.played = False

#    def deal_card(self):
#        c = self.game.shoe.get_next_card()
#        self.cards.append(c)

    def is_blackjack(self):
        if len(self.cards) != 2:
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

    def deal_card(self):
        self.cards.append(self.game.shoe.get_next_card())
        
    def is_busted(self):
        return self.get_value(CountMethod.Soft) > 21

    def get_value(self, count_method):
        v = 0
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
            if not self.payed:
                if self.is_busted():
                    self.payed = True
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

    def __str__(self):
        out = ' '
        for i in range(len(self.cards)):
            out = '%s%s ' % (out, self.cards[i])
        out = '%s ⇒  %s ' % (out, self.get_value(CountMethod.Soft))
        if self.status == HandStatus.Lost:
            out = '%s-' % out
        elif self.status == HandStatus.Won:
            out = '%s+' % out
        out = '%s$%s' % (out, self.bet / 100.0)
        if not self.played and self == self.game.player_hands[self.game.current_player_hand]:
            out = '%s ⇐' % out
        out = '%s ' % out
        if self.status == HandStatus.Lost:
            out = '%s%s' % (out, 'Busted!' if self.is_busted() else 'Lose!')
        elif self.status == HandStatus.Won:
            out = '%s%s' % (out, 'Blackjack!' if self.is_blackjack() else 'Win!')
        elif self.status == HandStatus.Push:
            out = '%s%s' % (out, 'Push!')
        out = '%s\n\n' % out
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

    def deal_card(self):
        c = self.game.shoe.get_next_card()
        self.cards.append(c)

    def is_busted(self):
        return self.get_value(CountMethod.Soft) > 21

    def get_value(self, count_method):
        v = 0
        total = 0
        for x in range(len(self.cards)):
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
            if i == 1 and self.hide_down_card:
                out = '%s%s ' % (out, Card.faces[13][0])
            else:
                c = self.cards[i]
                out = '%s%s ' % (out, Card.faces[c.value][c.suite])
        out = '%s ⇒  %s' % (out, self.get_value(CountMethod.Soft))
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
