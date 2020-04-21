
import os, sys, tty, termios
from copy import copy
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
    termios_attrs = None
    
    def __init__(self):
        self.num_decks = 1
        self.money = 10000
        self.current_bet = 500
        self.load_game()
        self.shoe = Shoe(self.num_decks)
        self.dealer_hand = None
        self.current_player_hand = 0
        self.player_hands = []

    def __del__(self):
        Game.buffer()

    def unbuffer():
        Game.termios_attrs = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())

    def buffer():
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, Game.termios_attrs)

    def all_bets(self):
        bets = 0
        for x in range(len(self.player_hands)):
            bets += self.player_hands[x].bet
        return bets

    def ask_insurance(self):
        print(' Insurance?  (Y) Yes  (N) No')
        br = False
        c = ''
        while True:
            c = sys.stdin.read(1)
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
            self.bet_options()
            return
        self.draw_hands()
        self.player_hands[0].get_action()
        self.save_game()

    def draw_hands(self):
        self.clear()
        out = '\n Dealer:\n%s\n' % str(self.dealer_hand)
        out = '%s\n Player $%.2f:\n' % (out, self.money / 100.0)
        for i in range(len(self.player_hands)):
            out = '%s%s' % (out, str(self.player_hands[i]))
        print(u'%s' % out)

    def bet_options(self):
        print(' (D) Deal Hand  (B) Change Bet  (O) Options  (Q) Quit')
        br = False
        c = ''
        while True:
            c = sys.stdin.read(1)
            if c == 'd':
                br = True
                self.deal_new_hand()
            elif c == 'b':
                br = True
                self.get_new_bet()
            elif c == 'o':
                br = True
                self.game_options()
            elif c == 'q':
                br = True
                self.clear()
            if br:
                break

    def game_options(self):
        self.clear()
        self.draw_hands()
        print(' (N) Number of Decks  (T) Deck Type  (B) Back')
        br = False
        c = ''
        while True:
            c = sys.stdin.read(1)
            if c == 'n':
                br = True
                self.get_new_num_decks()
            elif c == 't':
                br = True
                self.get_new_deck_type()
            elif c == 'b':
                br = True
                self.clear()
                self.draw_hands()
                self.bet_options()
            if br:
                break

    def get_new_num_decks(self):
        self.clear()
        self.draw_hands()
        print('  Number of Decks: %d  Enter New Number of Decks (1-8): ' % self.num_decks)
        tmp = int(sys.stdin.read(1))
        if tmp < 1:
            tmp = 1
        if tmp > 8:
            tmp = 8
        self.game.num_decks = tmp
        self.game_options()

    def get_new_deck_type(self):
        self.clear()
        self.draw_hands()
        print(' (1) Regular  (2) Aces  (3) Jacks  (4) Aces & Jacks  (5) Sevens  (6) Eights')
        br = False
        c = ''
        while True:
            c = sys.stdin.read(1)
            if c == '1':
                br = True
                self.shoe.new_regular()
            if c == '2':
                br = True
                self.shoe.new_aces()
            if c == '3':
                br = True
                self.shoe.new_jacks()
            if c == '4':
                br = True
                self.shoe.new_aces_jacks()
            if c == '5':
                br = True
                self.shoe.new_sevens()
            if c == '6':
                br = True
                self.shoe.new_eights()
            if br:
                self.draw_hands()
                self.bet_options()
                break

    def get_new_bet(self):
        self.clear()
        self.draw_hands()
        print('  Current Bet: $%.2f  Enter New Bet: $' % (self.current_bet / 100.0))
        Game.buffer()
        tmp = input()
        Game.unbuffer()
        self.current_bet = int(tmp) * 100
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
        self.bet_options()

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
            self.bet_options()
            return
        h = self.player_hands[self.current_player_hand]
        if h.is_done():
            self.play_dealer_hand()
            self.draw_hands()
            self.bet_options()
            return
        self.draw_hands()
        h.get_action()

    def normalize_bet(self):
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
        self.normalize_bet()
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
        Game.unbuffer()
        self.deal_new_hand()
        Game.buffer()

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
            s = f.read().strip()
            f.close()
        a = s.split('|')
        if len(a) == 3:
            self.num_decks = int(a[0])
            self.money = float(a[1])
            self.current_bet = int(float(a[2]))
        if self.money < Game.min_bet:
            self.money = 10000
            self.current_bet = Game.min_bet

    def split_current_hand(self):
        hand_count = len(self.player_hands)
        new_hand = PlayerHand(self, self.current_bet)
        self.player_hands.append(new_hand)

        while hand_count > self.current_player_hand:
            h = copy(self.player_hands[hand_count - 1])
            self.player_hands[hand_count] = h
            hand_count -= 1

        current_hand = self.player_hands[self.current_player_hand]
        split_hand = self.player_hands[self.current_player_hand + 1]

        split_hand.cards = [copy(current_hand.cards[1])]
        current_hand.cards = [copy(current_hand.cards[0])]
        current_hand.deal_card()

        if current_hand.is_done():
            current_hand.process()
            return

        self.draw_hands()
        current_hand.get_action()

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
            out = '%s%s ' % (out, self.cards[i])
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
        c = ''
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

class DealerHand(Hand):

    def __init__(self, game):
        super().__init__(game)
        self.hide_down_card = True

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
                out = '%s%s ' % (out, Card.faces[c.value][c.suit])
        out = '%s ⇒  %s' % (out, self.get_value(CountMethod.Soft))
        return u'%s' % out

    def upcard_is_ace(self):
        return self.cards[0].is_ace()

class Shoe:

    shuffle_specs = [80, 81, 82, 84, 86, 89, 92]

    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.cards = []

    def need_to_shuffle(self):
        if len(self.cards) == 0:
            return True
        total_cards = self.num_decks * 52
        cards_dealt = total_cards - len(self.cards)
        used = (cards_dealt / total_cards) * 100.0

        return used > Shoe.shuffle_specs[self.num_decks - 1]

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
            for suit in range(4):
                for value in range(13):
                    self.cards.append(Card(value, suit))

    def new_aces(self):
        self.cards = []
        for _ in range(self.num_decks * 10):
            for suit in range(4):
                self.cards.append(Card(0, suit))

    def new_jacks(self):
        self.cards = []
        for _ in range(self.num_decks * 10):
            for suit in range(4):
                self.cards.append(Card(10, suit))

    def new_aces_jacks(self):
        self.cards = []
        for _ in range(self.num_decks * 10):
            for suit in range(4):
                self.cards.append(Card(0, suit))
                self.cards.append(Card(10, suit))

    def new_sevens(self):
        self.cards = []
        for _ in range(self.num_decks * 10):
            for suit in range(4):
                self.cards.append(Card(6, suit))

    def new_eights(self):
        self.cards = []
        for _ in range(self.num_decks * 10):
            for suit in range(4):
                self.cards.append(Card(7, suit))

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

    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        return u'%s' % Card.faces[self.value][self.suit]

    def is_ace(self):
        return self.value == 0

    def is_ten(self):
        return self.value > 8
