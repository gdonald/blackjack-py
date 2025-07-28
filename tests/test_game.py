import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock, patch, mock_open
from bj.game import Game
from bj.player_hand import PlayerHand, HandStatus
from bj.dealer_hand import DealerHand
from bj.hand import CountMethod
from bj.card import Card
from bj.shoe import Shoe


class TestGame(unittest.TestCase):

    def setUp(self):
        with patch("bj.game.Game.load_game"):
            self.game = Game()

    def test_game_initialization(self):
        self.assertIsInstance(self.game.shoe, Shoe)
        self.assertEqual(self.game.deck_type, 1)
        self.assertEqual(self.game.face_type, 1)
        self.assertEqual(self.game.money, 10000)
        self.assertEqual(self.game.current_bet, 500)
        self.assertIsNone(self.game.dealer_hand)
        self.assertEqual(self.game.current_player_hand, 0)
        self.assertEqual(self.game.player_hands, [])
        self.assertFalse(self.game.quitting)

    def test_class_constants(self):
        self.assertEqual(Game.save_file, "bj.txt")
        self.assertEqual(Game.min_bet, 500)
        self.assertEqual(Game.max_bet, 10000000)

    def test_all_bets(self):
        hand1 = Mock()
        hand1.bet = 500
        hand2 = Mock()
        hand2.bet = 1000
        hand3 = Mock()
        hand3.bet = 750

        self.game.player_hands = [hand1, hand2, hand3]

        total_bets = self.game.all_bets()
        self.assertEqual(total_bets, 2250)

    def test_all_bets_empty_hands(self):
        self.game.player_hands = []
        self.assertEqual(self.game.all_bets(), 0)

    def test_card_face_type_1(self):
        self.game.face_type = 1
        face = self.game.card_face(0, 0)
        self.assertEqual(face, Card.faces[0][0])

    def test_card_face_type_2(self):
        self.game.face_type = 2
        face = self.game.card_face(0, 0)
        self.assertEqual(face, Card.faces2[0][0])

    @patch("bj.game.clear")
    def test_draw_hands(self, mock_clear):
        dealer_hand = Mock()
        dealer_hand.__str__ = Mock(return_value="Dealer: A♠ ?? ⇒ 11")

        player_hand = Mock()
        player_hand.__str__ = Mock(return_value="Player: K♥ 5♣ ⇒ 15 $5.00")

        self.game.dealer_hand = dealer_hand
        self.game.player_hands = [player_hand]
        self.game.money = 10000

        with patch("builtins.print") as mock_print:
            self.game.draw_hands()

            mock_clear.assert_called_once()
            mock_print.assert_called_once()

            printed_output = mock_print.call_args[0][0]
            self.assertIn("Dealer:", printed_output)
            self.assertIn("Player $100.00:", printed_output)

    def test_normalize_bet_too_low(self):
        self.game.current_bet = 100
        self.game.normalize_bet()
        self.assertEqual(self.game.current_bet, Game.min_bet)

    def test_normalize_bet_too_high(self):
        self.game.money = 20000000
        self.game.current_bet = 20000000
        self.game.normalize_bet()
        self.assertEqual(self.game.current_bet, Game.max_bet)

    def test_normalize_bet_exceeds_money(self):
        self.game.money = 1000
        self.game.current_bet = 2000
        self.game.normalize_bet()
        self.assertEqual(self.game.current_bet, 1000)

    def test_normalize_bet_valid(self):
        self.game.money = 10000
        self.game.current_bet = 1000
        self.game.normalize_bet()
        self.assertEqual(self.game.current_bet, 1000)

    def test_more_hands_to_play_true(self):
        self.game.player_hands = [Mock(), Mock(), Mock()]
        self.game.current_player_hand = 1
        self.assertTrue(self.game.more_hands_to_play())

    def test_more_hands_to_play_false(self):
        self.game.player_hands = [Mock(), Mock(), Mock()]
        self.game.current_player_hand = 2
        self.assertFalse(self.game.more_hands_to_play())

    def test_need_to_play_dealer_hand_true(self):
        hand1 = Mock()
        hand1.is_busted.return_value = False
        hand1.is_blackjack.return_value = False

        hand2 = Mock()
        hand2.is_busted.return_value = True
        hand2.is_blackjack.return_value = False

        self.game.player_hands = [hand1, hand2]
        self.assertTrue(self.game.need_to_play_dealer_hand())

    def test_need_to_play_dealer_hand_false(self):
        hand1 = Mock()
        hand1.is_busted.return_value = True
        hand1.is_blackjack.return_value = False

        hand2 = Mock()
        hand2.is_busted.return_value = False
        hand2.is_blackjack.return_value = True

        self.game.player_hands = [hand1, hand2]
        self.assertFalse(self.game.need_to_play_dealer_hand())

    def test_pay_hands_player_wins(self):
        dealer_hand = Mock()
        dealer_hand.get_value.return_value = 18
        dealer_hand.is_busted.return_value = False
        self.game.dealer_hand = dealer_hand

        player_hand = Mock()
        player_hand.paid = False
        player_hand.get_value.return_value = 20
        player_hand.is_blackjack.return_value = False
        player_hand.bet = 1000

        self.game.player_hands = [player_hand]
        self.game.money = 10000

        with patch.object(self.game, "normalize_bet"):
            with patch.object(self.game, "save_game"):
                self.game.pay_hands()

                self.assertTrue(player_hand.paid)
                self.assertEqual(player_hand.status, HandStatus.Won)
                self.assertEqual(self.game.money, 11000)

    def test_pay_hands_player_loses(self):
        dealer_hand = Mock()
        dealer_hand.get_value.return_value = 20
        dealer_hand.is_busted.return_value = False
        self.game.dealer_hand = dealer_hand

        player_hand = Mock()
        player_hand.paid = False
        player_hand.get_value.return_value = 18
        player_hand.is_blackjack.return_value = False
        player_hand.bet = 1000

        self.game.player_hands = [player_hand]
        self.game.money = 10000

        with patch.object(self.game, "normalize_bet"):
            with patch.object(self.game, "save_game"):
                self.game.pay_hands()

                self.assertTrue(player_hand.paid)
                self.assertEqual(player_hand.status, HandStatus.Lost)
                self.assertEqual(self.game.money, 9000)

    def test_pay_hands_push(self):
        dealer_hand = Mock()
        dealer_hand.get_value.return_value = 20
        dealer_hand.is_busted.return_value = False
        self.game.dealer_hand = dealer_hand

        player_hand = Mock()
        player_hand.paid = False
        player_hand.get_value.return_value = 20
        player_hand.is_blackjack.return_value = False
        player_hand.bet = 1000

        self.game.player_hands = [player_hand]
        self.game.money = 10000

        with patch.object(self.game, "normalize_bet"):
            with patch.object(self.game, "save_game"):
                self.game.pay_hands()

                self.assertTrue(player_hand.paid)
                self.assertEqual(player_hand.status, HandStatus.Push)
                self.assertEqual(self.game.money, 10000)

    def test_pay_hands_blackjack_bonus(self):
        dealer_hand = Mock()
        dealer_hand.get_value.return_value = 18
        dealer_hand.is_busted.return_value = False
        self.game.dealer_hand = dealer_hand

        player_hand = Mock()
        player_hand.paid = False
        player_hand.get_value.return_value = 21
        player_hand.is_blackjack.return_value = True
        player_hand.bet = 1000

        self.game.player_hands = [player_hand]
        self.game.money = 10000

        with patch.object(self.game, "normalize_bet"):
            with patch.object(self.game, "save_game"):
                self.game.pay_hands()

                self.assertTrue(player_hand.paid)
                self.assertEqual(player_hand.status, HandStatus.Won)
                self.assertEqual(player_hand.bet, 1500)
                self.assertEqual(self.game.money, 11500)

    def test_pay_hands_dealer_busted(self):
        dealer_hand = Mock()
        dealer_hand.is_busted.return_value = True
        self.game.dealer_hand = dealer_hand

        player_hand = Mock()
        player_hand.paid = False
        player_hand.get_value.return_value = 18
        player_hand.is_blackjack.return_value = False
        player_hand.bet = 1000

        self.game.player_hands = [player_hand]
        self.game.money = 10000

        with patch.object(self.game, "normalize_bet"):
            with patch.object(self.game, "save_game"):
                self.game.pay_hands()

                self.assertTrue(player_hand.paid)
                self.assertEqual(player_hand.status, HandStatus.Won)
                self.assertEqual(self.game.money, 11000)

    def test_play_dealer_hand_blackjack(self):
        dealer_hand = Mock()
        dealer_hand.is_blackjack.return_value = True
        dealer_hand.hide_down_card = True
        dealer_hand.get_value.return_value = 21
        self.game.dealer_hand = dealer_hand

        with patch.object(self.game, "need_to_play_dealer_hand", return_value=False):
            with patch.object(self.game, "pay_hands"):
                self.game.play_dealer_hand()

                self.assertFalse(dealer_hand.hide_down_card)
                self.assertTrue(dealer_hand.played)

    def test_play_dealer_hand_no_need_to_play(self):
        dealer_hand = Mock()
        dealer_hand.is_blackjack.return_value = False
        self.game.dealer_hand = dealer_hand

        with patch.object(self.game, "need_to_play_dealer_hand", return_value=False):
            with patch.object(self.game, "pay_hands") as mock_pay:
                self.game.play_dealer_hand()

                self.assertTrue(dealer_hand.played)
                mock_pay.assert_called_once()

    def test_play_dealer_hand_hits_until_17(self):
        dealer_hand = Mock()
        dealer_hand.is_blackjack.return_value = False
        dealer_hand.hide_down_card = True
        dealer_hand.get_value.side_effect = [16, 16, 18, 18]
        self.game.dealer_hand = dealer_hand

        with patch.object(self.game, "need_to_play_dealer_hand", return_value=True):
            with patch.object(self.game, "pay_hands"):
                self.game.play_dealer_hand()

                self.assertFalse(dealer_hand.hide_down_card)
                dealer_hand.deal_card.assert_called_once()
                self.assertTrue(dealer_hand.played)

    def test_save_game_success(self):
        self.game.shoe.num_decks = 6
        self.game.money = 15000
        self.game.current_bet = 1000
        self.game.deck_type = 2
        self.game.face_type = 1

        expected_content = "6|15000|1000|2|1"

        with patch("builtins.open", mock_open()) as mock_file:
            self.game.save_game()

            mock_file.assert_called_once_with("bj.txt", "w")
            mock_file().write.assert_called_once_with(expected_content)

    def test_save_game_os_error(self):
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            self.game.save_game()

    def test_load_game_success(self):
        saved_data = "6|15000.0|1000.0|2|1"

        with patch("builtins.open", mock_open(read_data=saved_data)):
            self.game.load_game()

            self.assertEqual(self.game.shoe.num_decks, 6)
            self.assertEqual(self.game.money, 15000.0)
            self.assertEqual(self.game.current_bet, 1000)
            self.assertEqual(self.game.deck_type, 2)
            self.assertEqual(self.game.face_type, 1)

    def test_load_game_invalid_data(self):
        saved_data = "invalid|data"

        with patch("builtins.open", mock_open(read_data=saved_data)):

            original_money = self.game.money
            self.game.load_game()
            self.assertEqual(self.game.money, original_money)

    def test_load_game_file_not_found(self):
        with patch("builtins.open", side_effect=OSError("File not found")):

            original_money = self.game.money
            self.game.load_game()
            self.assertEqual(self.game.money, original_money)

    def test_load_game_low_money_reset(self):
        saved_data = "6|100.0|100.0|2|1"

        with patch("builtins.open", mock_open(read_data=saved_data)):
            self.game.load_game()

            self.assertEqual(self.game.money, 10000)
            self.assertEqual(self.game.current_bet, Game.min_bet)

    def test_split_current_hand(self):
        current_hand = Mock()
        current_hand.cards = [Card(6, 0), Card(6, 1)]

        self.game.player_hands = [current_hand]
        self.game.current_player_hand = 0
        self.game.current_bet = 1000

        with patch("bj.game.copy") as mock_copy:
            with patch.object(self.game, "draw_hands"):
                mock_copy.side_effect = lambda x: Mock() if isinstance(x, Card) else x

                self.game.split_current_hand()
                self.assertEqual(len(self.game.player_hands), 2)

                current_hand.deal_card.assert_called_once()

    def test_play_more_hands(self):
        hand1 = Mock()
        hand2 = Mock()
        hand2.is_done.return_value = False

        self.game.player_hands = [hand1, hand2]
        self.game.current_player_hand = 0

        with patch.object(self.game, "draw_hands"):
            self.game.play_more_hands()

            self.assertEqual(self.game.current_player_hand, 1)
            hand2.deal_card.assert_called_once()
            hand2.get_action.assert_called_once()

    def test_play_more_hands_done(self):
        hand1 = Mock()
        hand2 = Mock()
        hand2.is_done.return_value = True

        self.game.player_hands = [hand1, hand2]
        self.game.current_player_hand = 0

        self.game.play_more_hands()

        self.assertEqual(self.game.current_player_hand, 1)
        hand2.deal_card.assert_called_once()
        hand2.process.assert_called_once()


if __name__ == "__main__":
    unittest.main()
