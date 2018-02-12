#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bj'))

from BJ import Game

g = Game()
g.run()
