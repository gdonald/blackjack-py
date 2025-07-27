
from bj.hand import Hand, CountMethod

class DealerHand(Hand):

    def __init__(self, game):
        super().__init__(game)
        self.hide_down_card = True

    def is_busted(self):
        return self.get_value(CountMethod.Soft) > 21

    def get_value(self, count_method):
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
                out = '%s%s ' % (out, self.game.card_face(13, 0))
            else:
                c = self.cards[i]
                out = '%s%s ' % (out, self.game.card_face(c.value, c.suit))
        out = '%s ⇒  %s' % (out, self.get_value(CountMethod.Soft))
        return u'%s' % out

    def upcard_is_ace(self):
        return self.cards[0].is_ace()
