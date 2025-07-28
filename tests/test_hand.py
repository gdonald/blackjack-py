import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, MagicMock
from bj.hand import Hand, CountMethod
from bj.card import Card


class TestCountMethod(unittest.TestCase):

    def test_count_method_enum_values(self):
        self.assertEqual(CountMethod.Soft.value, 0)
        self.assertEqual(CountMethod.Hard.value, 1)


class TestHand(unittest.TestCase):

    def setUp(self):
        self.mock_game = Mock()
        self.mock_shoe = Mock()
        self.mock_game.shoe = self.mock_shoe
        self.hand = Hand(self.mock_game)

    def test_hand_initialization(self):
        self.assertEqual(self.hand.game, self.mock_game)
        self.assertEqual(self.hand.cards, [])
        self.assertFalse(self.hand.stood)
        self.assertFalse(self.hand.played)

    def test_deal_card(self):
        mock_card = Mock()
        self.mock_shoe.get_next_card.return_value = mock_card

        self.hand.deal_card()

        self.mock_shoe.get_next_card.assert_called_once()
        self.assertIn(mock_card, self.hand.cards)
        self.assertEqual(len(self.hand.cards), 1)

    def test_is_blackjack_true(self):
        ace = Card(0, 0)
        ten = Card(9, 1)
        self.hand.cards = [ace, ten]

        self.assertTrue(self.hand.is_blackjack())

        self.hand.cards = [ten, ace]
        self.assertTrue(self.hand.is_blackjack())

        jack = Card(10, 0)
        self.hand.cards = [ace, jack]
        self.assertTrue(self.hand.is_blackjack())

        queen = Card(11, 0)
        self.hand.cards = [ace, queen]
        self.assertTrue(self.hand.is_blackjack())

        king = Card(12, 0)
        self.hand.cards = [ace, king]
        self.assertTrue(self.hand.is_blackjack())

    def test_is_blackjack_false(self):
        ace = Card(0, 0)
        ten = Card(9, 1)
        two = Card(1, 0)

        self.hand.cards = [ace]
        self.assertFalse(self.hand.is_blackjack())

        self.hand.cards = [ace, ten, two]
        self.assertFalse(self.hand.is_blackjack())

        self.hand.cards = [ten, Card(9, 0)]
        self.assertFalse(self.hand.is_blackjack())

        self.hand.cards = [ace, two]
        self.assertFalse(self.hand.is_blackjack())

        self.hand.cards = []
        self.assertFalse(self.hand.is_blackjack())


if __name__ == "__main__":
    unittest.main()
