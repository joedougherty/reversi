from Board import Board
from midas import Node, find_max_nodes, add_children, add_level_to_game, simulate_turns

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

