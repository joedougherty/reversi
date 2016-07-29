# -*- coding: utf-8 -*-

from Board import Board
from midas import Node, find_max_nodes, add_children, add_level_to_game_tree, simulate_turns
from timeit import default_timer as timer

# Create a single-node game tree containing only the opening board:
#
#   | 0| 1| 2| 3| 4| 5| 6| 7|
#   --------------------------
#   0|  |  |  |  |  |  |  |  |
#   --------------------------
#   1|  |  |  |  |  |  |  |  |
#   --------------------------
#   2|  |  |  |  |  |  |  |  |
#   --------------------------
#   3|  |  |  |● |○ |  |  |  |
#   --------------------------
#   4|  |  |  |○ |● |  |  |  |
#   --------------------------
#   5|  |  |  |  |  |  |  |  |
#   --------------------------
#   6|  |  |  |  |  |  |  |  |
#   --------------------------
#   7|  |  |  |  |  |  |  |  |
#   --------------------------
game_tree = Node(Board(), parent=None)

def timetrial(num_of_turns):
	# https://stackoverflow.com/questions/7370801/measure-time-elapsed-in-python
	start = timer()

	game_tree = Node(Board(), parent=None)
	simulate_turns(game_tree, game_tree.board.BLACK, num_of_turns)

	end = timer()

	print("Simulating {} turns took {}".format(num_of_turns, (end-start)))
	print("Number of terminal nodes: {}\n".format(len(find_max_nodes(game_tree))))

for i in range(1,5):
	timetrial(i)

