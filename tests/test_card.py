import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bj.card import Card


class TestCard(unittest.TestCase):

    def test_card_initialization(self):
        card = Card(0, 0)
        self.assertEqual(card.value, 0)
        self.assertEqual(card.suit, 0)

        card = Card(12, 3)
        self.assertEqual(card.value, 12)
        self.assertEqual(card.suit, 3)

    def test_is_ace(self):
        ace = Card(0, 0)
        self.assertTrue(ace.is_ace())

        king = Card(12, 0)
        self.assertFalse(king.is_ace())

        two = Card(1, 0)
        self.assertFalse(two.is_ace())

    def test_is_ten(self):
        ten = Card(9, 0)
        self.assertTrue(ten.is_ten())

        jack = Card(10, 0)
        self.assertTrue(jack.is_ten())

        queen = Card(11, 0)
        self.assertTrue(queen.is_ten())

        king = Card(12, 0)
        self.assertTrue(king.is_ten())

        nine = Card(8, 0)
        self.assertFalse(nine.is_ten())

        ace = Card(0, 0)
        self.assertFalse(ace.is_ten())

    def test_faces_array_structure(self):

        self.assertEqual(len(Card.faces), 14)
        for face_group in Card.faces:
            self.assertEqual(len(face_group), 4)

    def test_faces2_array_structure(self):

        self.assertEqual(len(Card.faces2), 14)
        for face_group in Card.faces2:
            self.assertEqual(len(face_group), 4)


if __name__ == "__main__":
    unittest.main()
