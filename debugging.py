from midas import *
from Board import Board
game_tree = Node(Board(), None)
simulate_turns(game_tree, game_tree.board.BLACK, num_of_turns=3)
max_nodes = find_max_nodes(game_tree)
third = max_nodes[0]
render(third.board.matrix)

#simulate_turns(third, third.board.BLACK, num_of_turns=1)
#third_results = find_max_nodes(third)
#len(third_results)
