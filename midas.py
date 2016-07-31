from reversiutils import alternate_player
from Board import Board

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
    def __init__(self, board, parent=None, level=0):
        self.board = board
        self.children = []
        self.parent = parent
        self.level = level

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
            game_state.add_child(Node(new_board, parent=game_state, level=game_state.level + 1))

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

    If root_first == True:
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
        

