
import termios, sys, tty, os

from copy import copy

from bj.card import Card
from bj.dealer_hand import DealerHand
from bj.hand import CountMethod
from bj.player_hand import PlayerHand, HandStatus
from bj.shoe import Shoe

def clear():
    os.system('export TERM=linux; clear')

def buffer():
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, Game.termios_attrs)

def unbuffer():
    Game.termios_attrs = termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())

class Game:
    save_file = 'bj.txt'
    min_bet = 500
    max_bet = 10000000
    termios_attrs = None

    def __init__(self):
        self.shoe = Shoe()
        self.deck_type = 1
        self.face_type = 1
        self.money = 10000
        self.current_bet = 500
        self.load_game()
        self.dealer_hand = None
        self.current_player_hand = 0
        self.player_hands = []
        self.quitting = False

    def __del__(self):
        buffer()

    def all_bets(self):
        bets = 0
        for x in range(len(self.player_hands)):
            bets += self.player_hands[x].bet
        return bets

    def ask_insurance(self):
        print(' Insurance?  (Y) Yes  (N) No')
        br = False
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

    def card_face(self, value, suit):
        if self.face_type == 2:
            return Card.faces2[value][suit]
        return Card.faces[value][suit]

    def deal_new_hand(self):
        if self.shoe.need_to_shuffle():
            self.shoe.build_new_shoe(self.deck_type)
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
        clear()
        out = '\n Dealer:\n%s\n' % str(self.dealer_hand)
        out = '%s\n Player $%.2f:\n' % (out, self.money / 100.0)
        for i in range(len(self.player_hands)):
            out = '%s%s\n' % (out, str(self.player_hands[i]))
        print(u'%s' % out, end='')

    def bet_options(self):
        print(' (D) Deal Hand  (B) Change Bet  (O) Options  (Q) Quit')
        br = False
        while True:
            c = sys.stdin.read(1)
            if c == 'd':
                br = True
            elif c == 'b':
                br = True
                self.get_new_bet()
            elif c == 'o':
                br = True
                self.game_options()
            elif c == 'q':
                br = True
                self.quitting = True
                clear()
            if br:
                break

    def game_options(self):
        clear()
        self.draw_hands()
        print(' (N) Number of Decks  (T) Deck Type  (F) Face Type  (B) Back')
        br = False
        while True:
            c = sys.stdin.read(1)
            if c == 'n':
                br = True
                self.get_new_num_decks()
            elif c == 't':
                br = True
                self.get_new_deck_type()
            elif c == 'f':
                br = True
                self.get_new_face_type()
            elif c == 'b':
                br = True
                clear()
                self.draw_hands()
                self.bet_options()
            if br:
                break

    def get_new_num_decks(self):
        clear()
        self.draw_hands()
        print('  Number of Decks: %d  Enter New Number of Decks (1-8): ' % self.shoe.num_decks)
        tmp = int(sys.stdin.read(1))
        if tmp < 1:
            tmp = 1
        if tmp > 8:
            tmp = 8
        self.shoe.num_decks = tmp
        self.game_options()

    def get_new_face_type(self):
        clear()
        self.draw_hands()
        print('(1) A♠  (2) 🂡')
        br = False
        while True:
            c = sys.stdin.read(1)
            if c == '1' or c == '2':
                br = True
                self.face_type = int(c)
                self.save_game()
            if br:
                self.draw_hands()
                self.bet_options()
                break

    def get_new_deck_type(self):
        clear()
        self.draw_hands()
        print(' (1) Regular  (2) Aces  (3) Jacks  (4) Aces & Jacks  (5) Sevens  (6) Eights')
        br = False
        while True:
            tmp = sys.stdin.read(1)
            c = int(tmp)
            if 0 < c < 7:
                br = True
                self.deck_type = c
                if c > 1:
                    self.shoe.num_decks = 8
                self.shoe.build_new_shoe(self.deck_type)
                self.save_game()
            if br:
                self.draw_hands()
                self.bet_options()
                break

    def get_new_bet(self):
        clear()
        self.draw_hands()
        print('  Current Bet: $%.2f  Enter New Bet: $' % (self.current_bet / 100.0), end='')
        buffer()
        tmp = input()
        unbuffer()
        self.current_bet = int(tmp) * 100
        self.normalize_bet()
        self.deal_new_hand()

    def insure_hand(self):
        h = self.player_hands[self.current_player_hand]
        h.bet /= 2
        h.played = True
        h.paid = True
        h.stayed = HandStatus.Lost
        self.money -= h.bet
        self.draw_hands()
        self.bet_options()

    def more_hands_to_play(self):
        return self.current_player_hand < len(self.player_hands) - 1

    def need_to_play_dealer_hand(self):
        for x in range(len(self.player_hands)):
            h = self.player_hands[x]
            if not (h.is_busted() or h.is_blackjack()):
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
            if h.paid:
                continue
            h.paid = True
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
        unbuffer()
        while not self.quitting:
            self.deal_new_hand()
        buffer()

    def save_game(self):
        try:
            with open(Game.save_file, 'w') as f:
                f.write('%s|%s|%s|%s|%s' % (self.shoe.num_decks,
                                            self.money,
                                            self.current_bet,
                                            self.deck_type,
                                            self.face_type))
        except OSError:
            pass

    def load_game(self):
        s = ''
        try:
            with open(Game.save_file, 'r') as f:
                s = f.read().strip()
        except OSError:
            pass

        a = s.split('|')
        if len(a) == 5:
            self.shoe.num_decks = int(a[0])
            self.money = float(a[1])
            self.current_bet = int(float(a[2]))
            self.deck_type = int(a[3])
            self.face_type = int(a[4])
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
