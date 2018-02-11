#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bj'))

from BJ import *

s = Shoe(8)

if s.need_to_shuffle():
    s.shuffle()

c = s.get_next_card()
print(c)

c = s.get_next_card()
print(c)
