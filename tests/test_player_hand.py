import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock, patch
from bj.player_hand import PlayerHand, HandStatus
from bj.hand import CountMethod
from bj.card import Card


class TestHandStatus(unittest.TestCase):

    def test_hand_status_enum_values(self):
        self.assertEqual(HandStatus.Unknown.value, 0)
        self.assertEqual(HandStatus.Won.value, 1)
        self.assertEqual(HandStatus.Lost.value, 2)
        self.assertEqual(HandStatus.Push.value, 3)


class TestPlayerHand(unittest.TestCase):

    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.card_face = MagicMock(return_value="??")
        self.mock_game.money = 10000
        self.mock_game.player_hands = []
        self.mock_game.current_player_hand = 0
        self.mock_game.all_bets = MagicMock(return_value=500)
        self.bet = 500
        self.player_hand = PlayerHand(self.mock_game, self.bet)
        self.mock_game.player_hands = [self.player_hand]

    def test_player_hand_initialization(self):
        self.assertEqual(self.player_hand.game, self.mock_game)
        self.assertEqual(self.player_hand.bet, self.bet)
        self.assertEqual(self.player_hand.status, HandStatus.Unknown)
        self.assertFalse(self.player_hand.paid)
        self.assertEqual(self.player_hand.cards, [])
        self.assertFalse(self.player_hand.stood)
        self.assertFalse(self.player_hand.played)

    def test_max_player_hands_constant(self):
        self.assertEqual(PlayerHand.max_player_hands, 7)

    def test_is_busted_true(self):
        self.player_hand.cards = [
            Card(9, 0),
            Card(9, 1),
            Card(1, 0),
        ]
        self.assertTrue(self.player_hand.is_busted())

    def test_is_busted_false(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1)]
        self.assertFalse(self.player_hand.is_busted())

        self.player_hand.cards = [Card(0, 0), Card(9, 1)]
        self.assertFalse(self.player_hand.is_busted())

    def test_get_value_soft_count(self):
        self.player_hand.cards = [Card(0, 0), Card(5, 1)]
        self.assertEqual(self.player_hand.get_value(CountMethod.Soft), 17)

        self.player_hand.cards = [Card(0, 0), Card(5, 1), Card(4, 0)]
        self.assertEqual(self.player_hand.get_value(CountMethod.Soft), 12)

    def test_get_value_hard_count(self):
        self.player_hand.cards = [Card(0, 0), Card(5, 1)]
        self.assertEqual(self.player_hand.get_value(CountMethod.Hard), 7)

        self.player_hand.cards = [Card(10, 0), Card(11, 1)]
        self.assertEqual(self.player_hand.get_value(CountMethod.Hard), 20)

    def test_is_done_busted(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1), Card(1, 0)]

        result = self.player_hand.is_done()

        self.assertTrue(result)
        self.assertTrue(self.player_hand.played)
        self.assertTrue(self.player_hand.paid)
        self.assertEqual(self.player_hand.status, HandStatus.Lost)
        self.assertEqual(self.mock_game.money, 9500)

    def test_is_done_blackjack(self):
        self.player_hand.cards = [Card(0, 0), Card(9, 1)]

        result = self.player_hand.is_done()

        self.assertTrue(result)
        self.assertTrue(self.player_hand.played)

        self.assertFalse(self.player_hand.paid)

    def test_is_done_twenty_one(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1), Card(6, 2)]

        result = self.player_hand.is_done()

        self.assertTrue(result)
        self.assertTrue(self.player_hand.played)

    def test_is_done_stood(self):
        self.player_hand.stood = True

        result = self.player_hand.is_done()

        self.assertTrue(result)
        self.assertTrue(self.player_hand.played)

    def test_is_done_not_done(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1)]

        result = self.player_hand.is_done()

        self.assertFalse(result)
        self.assertFalse(self.player_hand.played)

    def test_can_split_valid(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1)]
        self.mock_game.all_bets.return_value = 500
        self.mock_game.money = 2000

        self.assertTrue(self.player_hand.can_split())

    def test_can_split_stood(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1)]
        self.player_hand.stood = True

        self.assertFalse(self.player_hand.can_split())

    def test_can_split_too_many_hands(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1)]
        self.mock_game.player_hands = [Mock() for _ in range(7)]

        self.assertFalse(self.player_hand.can_split())

    def test_can_split_insufficient_money(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1)]
        self.mock_game.all_bets.return_value = 1000
        self.mock_game.money = 1000

        self.assertFalse(self.player_hand.can_split())

    def test_can_split_different_values(self):
        self.player_hand.cards = [Card(6, 0), Card(7, 1)]

        self.assertFalse(self.player_hand.can_split())

    def test_can_split_not_two_cards(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1), Card(6, 2)]

        self.assertFalse(self.player_hand.can_split())

    def test_can_dbl_valid(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.mock_game.money = 2000
        self.mock_game.all_bets.return_value = 500

        self.assertTrue(self.player_hand.can_dbl())

    def test_can_dbl_insufficient_money(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.mock_game.money = 500
        self.mock_game.all_bets.return_value = 500

        self.assertFalse(self.player_hand.can_dbl())

    def test_can_dbl_stood(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.player_hand.stood = True

        self.assertFalse(self.player_hand.can_dbl())

    def test_can_dbl_not_two_cards(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1), Card(2, 0)]

        self.assertFalse(self.player_hand.can_dbl())

    def test_can_dbl_busted(self):
        self.player_hand.cards = [
            Card(9, 0),
            Card(9, 1),
        ]
        with patch.object(self.player_hand, "is_busted", return_value=True):
            self.assertFalse(self.player_hand.can_dbl())

    def test_can_dbl_blackjack(self):
        self.player_hand.cards = [Card(0, 0), Card(9, 1)]

        self.assertFalse(self.player_hand.can_dbl())

    def test_can_stand_valid(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]

        self.assertTrue(self.player_hand.can_stand())

    def test_can_stand_stood(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.player_hand.stood = True

        self.assertFalse(self.player_hand.can_stand())

    def test_can_stand_busted(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1), Card(1, 0)]

        self.assertFalse(self.player_hand.can_stand())

    def test_can_stand_blackjack(self):
        self.player_hand.cards = [Card(0, 0), Card(9, 1)]

        self.assertFalse(self.player_hand.can_stand())

    def test_can_hit_valid(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]

        self.assertTrue(self.player_hand.can_hit())

    def test_can_hit_played(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.player_hand.played = True

        self.assertFalse(self.player_hand.can_hit())

    def test_can_hit_stood(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.player_hand.stood = True

        self.assertFalse(self.player_hand.can_hit())

    def test_can_hit_twenty_one_hard(self):
        self.player_hand.cards = [Card(6, 0), Card(6, 1), Card(6, 2)]

        self.assertFalse(self.player_hand.can_hit())

    def test_can_hit_blackjack(self):
        self.player_hand.cards = [Card(0, 0), Card(9, 1)]

        self.assertFalse(self.player_hand.can_hit())

    def test_can_hit_busted(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1), Card(1, 0)]

        self.assertFalse(self.player_hand.can_hit())

    def test_hit_action(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        mock_card = Card(6, 0)

        with patch.object(self.player_hand, "deal_card") as mock_deal:
            with patch.object(self.player_hand, "is_done", return_value=False):
                with patch.object(self.player_hand, "get_action") as mock_get_action:
                    self.player_hand.hit()

                    mock_deal.assert_called_once()
                    self.mock_game.draw_hands.assert_called_once()
                    mock_get_action.assert_called_once()

    def test_hit_action_done(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1)]

        with patch.object(self.player_hand, "deal_card"):
            with patch.object(self.player_hand, "is_done", return_value=True):
                with patch.object(self.player_hand, "process") as mock_process:
                    self.player_hand.hit()

                    mock_process.assert_called_once()

    def test_dbl_action(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        original_bet = self.player_hand.bet

        with patch.object(self.player_hand, "deal_card"):
            with patch.object(self.player_hand, "is_done", return_value=True):
                with patch.object(self.player_hand, "process") as mock_process:
                    self.player_hand.dbl()

                    self.assertTrue(self.player_hand.played)
                    self.assertEqual(self.player_hand.bet, original_bet * 2)
                    mock_process.assert_called_once()

    def test_stand_action_more_hands(self):
        self.mock_game.more_hands_to_play.return_value = True

        self.player_hand.stand()

        self.assertTrue(self.player_hand.stood)
        self.assertTrue(self.player_hand.played)
        self.mock_game.play_more_hands.assert_called_once()

    def test_stand_action_no_more_hands(self):
        self.mock_game.more_hands_to_play.return_value = False

        self.player_hand.stand()

        self.assertTrue(self.player_hand.stood)
        self.assertTrue(self.player_hand.played)
        self.mock_game.play_dealer_hand.assert_called_once()
        self.mock_game.draw_hands.assert_called_once()
        self.mock_game.bet_options.assert_called_once()

    def test_str_representation_basic(self):
        self.player_hand.cards = [Card(0, 0), Card(9, 1)]
        self.player_hand.bet = 1000

        result = str(self.player_hand)

        self.assertIn("21", result)
        self.assertIn("$10.00", result)
        self.mock_game.card_face.assert_called()

    def test_str_representation_won_blackjack(self):
        self.player_hand.cards = [Card(0, 0), Card(9, 1)]
        self.player_hand.status = HandStatus.Won

        result = str(self.player_hand)

        self.assertIn("Blackjack!", result)

    def test_str_representation_won_regular(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1)]
        self.player_hand.status = HandStatus.Won

        result = str(self.player_hand)

        self.assertIn("Win!", result)
        self.assertNotIn("Blackjack!", result)

    def test_str_representation_lost_busted(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1), Card(1, 0)]
        self.player_hand.status = HandStatus.Lost

        result = str(self.player_hand)

        self.assertIn("Busted!", result)

    def test_str_representation_lost_regular(self):
        self.player_hand.cards = [Card(8, 0), Card(8, 1)]
        self.player_hand.status = HandStatus.Lost

        result = str(self.player_hand)

        self.assertIn("Lose!", result)
        self.assertNotIn("Busted!", result)

    def test_str_representation_push(self):
        self.player_hand.cards = [Card(9, 0), Card(9, 1)]
        self.player_hand.status = HandStatus.Push

        result = str(self.player_hand)

        self.assertIn("Push!", result)

    def test_str_representation_current_hand(self):
        self.player_hand.cards = [Card(4, 0), Card(5, 1)]
        self.player_hand.played = False
        self.mock_game.current_player_hand = 0

        result = str(self.player_hand)

        self.assertIn("⇐", result)


if __name__ == "__main__":
    unittest.main()
