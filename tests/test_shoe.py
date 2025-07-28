import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, Mock
from bj.shoe import Shoe
from bj.card import Card


class TestShoe(unittest.TestCase):

    def setUp(self):
        self.shoe = Shoe()

    def test_shoe_initialization(self):
        self.assertEqual(self.shoe.num_decks, 8)
        self.assertEqual(self.shoe.cards, [])
        self.assertEqual(self.shoe.cards_per_deck, 52)

    def test_shuffle_specs(self):
        expected_specs = [80, 81, 82, 84, 86, 89, 92, 95]
        self.assertEqual(Shoe.shuffle_specs, expected_specs)

    def test_need_to_shuffle_empty_cards(self):
        self.shoe.cards = []
        self.assertTrue(self.shoe.need_to_shuffle())

    def test_need_to_shuffle_under_threshold(self):
        self.shoe.cards = [Mock() for _ in range(21)]
        self.assertFalse(self.shoe.need_to_shuffle())

        self.shoe.cards = [Mock() for _ in range(20)]
        self.assertTrue(self.shoe.need_to_shuffle())

    def test_need_to_shuffle_different_deck_counts(self):
        self.shoe.num_decks = 1
        self.shoe.cards = [Mock() for _ in range(11)]
        self.assertFalse(self.shoe.need_to_shuffle())

        self.shoe.cards = [Mock() for _ in range(10)]
        self.assertTrue(self.shoe.need_to_shuffle())

    @patch("random.shuffle")
    def test_shuffle(self, mock_shuffle):
        self.shoe.cards = [Mock() for _ in range(10)]
        self.shoe.shuffle()
        self.assertEqual(mock_shuffle.call_count, 7)

    def test_get_next_card(self):
        mock_cards = [Mock() for _ in range(5)]
        self.shoe.cards = mock_cards.copy()

        first_card = self.shoe.get_next_card()
        self.assertEqual(first_card, mock_cards[0])
        self.assertEqual(len(self.shoe.cards), 4)
        self.assertNotIn(first_card, self.shoe.cards)

    def test_get_total_cards(self):
        self.shoe.num_decks = 6
        self.assertEqual(self.shoe.get_total_cards(), 312)

        self.shoe.num_decks = 1
        self.assertEqual(self.shoe.get_total_cards(), 52)

    def test_new_shoe(self):
        values = [0, 1, 2]
        self.shoe.num_decks = 2
        self.shoe.new_shoe(values)

        self.assertEqual(len(self.shoe.cards), 104)

        values_present = set(card.value for card in self.shoe.cards)
        self.assertTrue(values_present.issubset(set(values)))

    def test_new_regular(self):
        self.shoe.num_decks = 1
        self.shoe.new_regular()

        self.assertEqual(len(self.shoe.cards), 52)

        values_present = set(card.value for card in self.shoe.cards)
        self.assertEqual(values_present, set(range(13)))

    def test_new_aces(self):
        self.shoe.num_decks = 1
        self.shoe.new_aces()

        self.assertEqual(len(self.shoe.cards), 52)

        for card in self.shoe.cards:
            self.assertEqual(card.value, 0)

    def test_new_jacks(self):
        self.shoe.num_decks = 1
        self.shoe.new_jacks()

        self.assertEqual(len(self.shoe.cards), 52)

        for card in self.shoe.cards:
            self.assertEqual(card.value, 10)

    def test_new_aces_jacks(self):
        self.shoe.num_decks = 1
        self.shoe.new_aces_jacks()

        self.assertEqual(len(self.shoe.cards), 52)

        values_present = set(card.value for card in self.shoe.cards)
        self.assertEqual(values_present, {0, 10})

    def test_new_sevens(self):
        self.shoe.num_decks = 1
        self.shoe.new_sevens()

        self.assertEqual(len(self.shoe.cards), 52)

        for card in self.shoe.cards:
            self.assertEqual(card.value, 6)

    def test_new_eights(self):
        self.shoe.num_decks = 1
        self.shoe.new_eights()

        self.assertEqual(len(self.shoe.cards), 52)

        for card in self.shoe.cards:
            self.assertEqual(card.value, 7)

    @patch.object(Shoe, "shuffle")
    def test_build_new_shoe_regular(self, mock_shuffle):
        self.shoe.build_new_shoe(1)
        self.assertEqual(len(self.shoe.cards), 416)
        mock_shuffle.assert_called_once()

    @patch.object(Shoe, "shuffle")
    def test_build_new_shoe_aces(self, mock_shuffle):
        self.shoe.build_new_shoe(2)
        self.assertEqual(len(self.shoe.cards), 416)

        for card in self.shoe.cards:
            self.assertEqual(card.value, 0)
        mock_shuffle.assert_called_once()

    @patch.object(Shoe, "shuffle")
    def test_build_new_shoe_invalid_type(self, mock_shuffle):
        self.shoe.build_new_shoe(99)
        self.assertEqual(len(self.shoe.cards), 416)
        mock_shuffle.assert_called_once()


if __name__ == "__main__":
    unittest.main()
