from reversiutils import alternate_player, render
from Board import Board
from copy import deepcopy
from collections import namedtuple
from timeit import default_timer as timer

"""
This first section includes the basic Node class
and functions related to generating game trees.

These functions move from specific to general.

    add_children: a function that finds response boards, is the most specific.

    add_level_to_game_tree: runs `add_children` on all leaf nodes (as found by
    `find_max_nodes`)

    simulate_turns: calls `add_level_to_game_tree` for the current player, 
    then the opponent, as many as times as indicated by the num_of_turns argument.
"""

class Node():
    def __init__(self, board, parent=None, level=0, placed_piece=None, player=None, next_player=None):
        self.board = board
        self.children = []
        self.parent = parent
        self.level = level
        self.placed_piece = placed_piece
        self.player = player
        self.next_player = next_player

    def add_child(self, obj):
        self.children.append(obj)

    def is_a_leaf_node(self):
        return self.children == []

    def is_the_root_node(self):
        return self.parent is None

def add_children(game_state, current_player):
    """ 
    Given a game state (in the form of a Node object):
        * calculate all possible responses as given by `current_player`
        * attach them as children to the provided game state
    """
    seen_moves = []

    legal_moves = game_state.board.find_legal_moves(current_player)
    for proposed_move in legal_moves:
        # A move (proposed_move.coordinates) occassionally comes up more than once.
        # However, we only want to generate one board per proposed_move.
        #
        # A new board will only be created if proposed_move.coordinates
        # has not been seen yet.    
        if proposed_move.coordinates not in seen_moves:
            seen_moves.append(proposed_move.coordinates) # keeps track of proposed_move.coordindates

            new_board = game_state.board.update(proposed_move.coordinates, current_player, legal_moves)
            node = Node(
                new_board, 
                parent=game_state, 
                level=game_state.level+1, 
                placed_piece = proposed_move.coordinates,
                player=current_player, 
                next_player=alternate_player(current_player)
            )
            game_state.add_child(node)

def add_level_to_game_tree(game_tree, current_player):
    """ 
    For all terminal nodes in the game tree:
        * run `add_children` on each
    """
    for terminal_node in find_max_nodes(game_tree):
        add_children(terminal_node, current_player)
    return game_tree

def simulate_turns(root_node, current_player, num_of_turns=1):
    """ 
    For each turn as given by num_of_turns:
        * Add all possible responses to terminal nodes for current player
        * Add all possible responses to terminal nodes for opponent
    """
    while num_of_turns > 0:
        add_level_to_game_tree(root_node, current_player)
        add_level_to_game_tree(root_node, alternate_player(current_player))
        num_of_turns = num_of_turns - 1
    return root_node

"""
This section includes functions that facilitate game tree analysis.
"""

def find_max_depth(root_node):
    leaf_nodes = find_max_nodes(root_node)
    return max([node.level for node in leaf_nodes])

def find_min_depth(root_node):
    leaf_nodes = find_max_nodes(root_node)
    return min([node.level for node in leaf_nodes])

def find_max_nodes(root_node, max_nodes=None):
    """
    Recursively traverse the game tree (starting from root_node)
    and collect references to all terminal nodes.

    Return a list of references to all terminal nodes.
    """
    if max_nodes is None:
        max_nodes = []

    try:
        if root_node.is_a_leaf_node():
            max_nodes.append(root_node)
        else:
            for child in root_node.children:
                find_max_nodes(child, max_nodes)
    except Exception as e:
        raise e
    finally:
        return max_nodes

def trace_lineage(node, root_first_order=True):
    """ 
    Traces a node back to the opening board.

    Returns a list of previous board states, including
    the opening board.

    If root_first_order == True:
        The returned list will start with the opening board
        and move toward `node`
    Otherwise:
        The returned list will start with `node` and move
        toward the opening board
    """

    lineage = []
    while not node.is_the_root_node():
        lineage.append(node)
        node = node.parent

    # Add the opening board to lineage
    lineage.append(Node(Board()))

    if root_first_order:
        lineage.reverse()
    
    return lineage
        
def show_lineage(lineage):
    for node in lineage:
        render(node.board.matrix)

def this_is_a_final_state(node):
    opponent = alternate_player(node.player) 
    
    opponent_has_legal_moves = node.board.find_legal_moves(opponent) != []
    current_player_has_legal_moves = node.board.find_legal_moves(node.player) != []
    
    if opponent_has_legal_moves or current_player_has_legal_moves:
        return False
    return True

""" AI """

def decide_move(current_game_state, current_player, num_of_turns_to_lookahead=2, debug=False):
    start = timer()

    # Generate temporary game tree (of depth given by num_of_turns_to_lookahead)
    root_node = deepcopy(current_game_state)
    game_tree = simulate_turns(root_node, current_player, num_of_turns=num_of_turns_to_lookahead)

    # Apply minimax to game tree
    v = minimax(game_tree, max_player=current_player, min_player=alternate_player(current_player))

    # Once the optimal board is found,
    # trace it back to the move immediately
    # following the root node
    node_containing_next_move = trace_lineage(v.node)[1]

    # Clean up the temporary game tree
    del root_node, game_tree

    if debug:
        print(v)

    # Return the spot to move that's associated
    # with the best score according to minimax

    end = timer()
    print('Opponent took {} seconds to respond.'.format((end-start)))
    print('Opponent moved to location {}.\n'.format(node_containing_next_move.placed_piece))

    return node_containing_next_move.placed_piece

def evaluate(node, player):
    opponent = alternate_player(player)

    current_player_has_most_pieces = node.board.count_pieces(player) > node.board.count_pieces(opponent)
    opponent_has_most_pieces = node.board.count_pieces(player) < node.board.count_pieces(opponent)

    if node.board.game_is_over(player):
        if current_player_has_most_pieces:
            return 10000000
        elif opponent_has_most_pieces:
            return -10000000
        else: # game is a draw
            return 0
    else:
        return node.board.count_pieces(player) 

terminal_node = namedtuple('terminal_node', ['node', 'val'])

def minimax(node, max_player=None, min_player=None):
    """
    Implementation translated from pseudocode found on
    https://www.cs.cornell.edu/courses/cs312/2002sp/lectures/rec21.htm 

    fun minimax(n: node): int =
    if leaf(n) then return evaluate(n)
    if n is a max node
      v := L
      for each child of n
         v' := minimax (child)
         if v' > v, v:= v'
      return v
    if n is a min node
      for each child of n
         v' := minimax (child)
         if v' < v, v:= v'
      return v

    """

    if node.is_a_leaf_node():
        return terminal_node(node, evaluate(node, player=max_player))

    if node.next_player == max_player:
        best_case = terminal_node(None, -1000000)
        for child in node.children:
            v = minimax(child, max_player=max_player, min_player=min_player)
            if v.val > best_case.val:
                best_case = v
        return best_case
    elif node.next_player == min_player:
        worst_case = terminal_node(None, 1000000)
        for child in node.children:
            v = minimax(child, max_player=max_player, min_player=min_player)
            if v.val < worst_case.val:
                worst_case = v
        return worst_case
    else:
        raise ValueError('node.next_player was set to neither max_player nor min_player.')

