import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock
from bj.dealer_hand import DealerHand
from bj.hand import CountMethod
from bj.card import Card


class TestDealerHand(unittest.TestCase):

    def setUp(self):
        self.mock_game = Mock()
        self.mock_game.card_face = MagicMock(return_value="??")
        self.dealer_hand = DealerHand(self.mock_game)

    def test_dealer_hand_initialization(self):
        self.assertEqual(self.dealer_hand.game, self.mock_game)
        self.assertEqual(self.dealer_hand.cards, [])
        self.assertFalse(self.dealer_hand.stood)
        self.assertFalse(self.dealer_hand.played)
        self.assertTrue(self.dealer_hand.hide_down_card)

    def test_is_busted_true(self):
        self.dealer_hand.cards = [
            Card(9, 0),
            Card(9, 1),
            Card(1, 0),
        ]
        self.dealer_hand.hide_down_card = False
        self.assertTrue(self.dealer_hand.is_busted())

    def test_is_busted_false(self):
        self.dealer_hand.cards = [Card(9, 0), Card(9, 1)]
        self.dealer_hand.hide_down_card = False
        self.assertFalse(self.dealer_hand.is_busted())

        self.dealer_hand.cards = [Card(0, 0), Card(9, 1)]
        self.assertFalse(self.dealer_hand.is_busted())

    def test_get_value_hidden_down_card(self):
        self.dealer_hand.cards = [Card(9, 0), Card(0, 1)]
        self.dealer_hand.hide_down_card = True

        self.assertEqual(self.dealer_hand.get_value(CountMethod.Soft), 10)
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Hard), 10)

    def test_get_value_soft_count(self):
        self.dealer_hand.hide_down_card = False

        self.dealer_hand.cards = [Card(0, 0), Card(5, 1)]
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Soft), 17)

        self.dealer_hand.cards = [Card(0, 0), Card(5, 1), Card(4, 0)]
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Soft), 12)

        self.dealer_hand.cards = [Card(0, 0), Card(0, 1)]
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Soft), 12)

    def test_get_value_hard_count(self):
        self.dealer_hand.hide_down_card = False

        self.dealer_hand.cards = [Card(0, 0), Card(5, 1)]
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Hard), 7)

        self.dealer_hand.cards = [Card(0, 0), Card(0, 1)]
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Hard), 2)

        self.dealer_hand.cards = [Card(10, 0), Card(11, 1), Card(12, 0)]
        self.assertEqual(self.dealer_hand.get_value(CountMethod.Hard), 30)

    def test_get_value_soft_over_21_fallback(self):
        self.dealer_hand.hide_down_card = False

        self.dealer_hand.cards = [Card(0, 0), Card(5, 1), Card(5, 0)]
        soft_value = self.dealer_hand.get_value(CountMethod.Soft)
        hard_value = self.dealer_hand.get_value(CountMethod.Hard)

        self.assertEqual(soft_value, 13)
        self.assertEqual(hard_value, 13)

    def test_str_representation_hidden_card(self):
        self.dealer_hand.cards = [Card(0, 0), Card(9, 1)]
        self.dealer_hand.hide_down_card = True

        result = str(self.dealer_hand)

        self.mock_game.card_face.assert_any_call(0, 0)
        self.mock_game.card_face.assert_any_call(13, 0)
        self.assertIn("11", result)

    def test_str_representation_revealed_cards(self):
        self.dealer_hand.cards = [Card(0, 0), Card(9, 1)]
        self.dealer_hand.hide_down_card = False

        result = str(self.dealer_hand)

        self.mock_game.card_face.assert_any_call(0, 0)
        self.mock_game.card_face.assert_any_call(9, 1)
        self.assertIn("21", result)

    def test_upcard_is_ace_true(self):
        self.dealer_hand.cards = [Card(0, 0), Card(9, 1)]
        self.assertTrue(self.dealer_hand.upcard_is_ace())

    def test_upcard_is_ace_false(self):
        self.dealer_hand.cards = [Card(9, 0), Card(0, 1)]
        self.assertFalse(self.dealer_hand.upcard_is_ace())

        self.dealer_hand.cards = []
        with self.assertRaises(IndexError):
            self.dealer_hand.upcard_is_ace()

    def test_ten_value_cards(self):
        self.dealer_hand.hide_down_card = False

        for value in [9, 10, 11, 12]:
            self.dealer_hand.cards = [Card(value, 0)]
            self.assertEqual(self.dealer_hand.get_value(CountMethod.Hard), 10)

    def test_number_cards_value(self):
        self.dealer_hand.hide_down_card = False

        for value in range(1, 9):
            self.dealer_hand.cards = [Card(value, 0)]
            expected_value = value + 1
            self.assertEqual(
                self.dealer_hand.get_value(CountMethod.Hard), expected_value
            )


if __name__ == "__main__":
    unittest.main()
