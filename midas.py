from reversiutils import alternate_player, render, validate_proposed_move

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

def find_max_nodes(root_node, max_nodes=None):
    """
    Recursively traverse the game tree (starting from root_node)
    and collect references to all terminal nodes.

    Return a list of references to all terminal nodes.
    """
    if max_nodes is None:
        max_nodes = []

    try:
        if root_node.children == []:
            max_nodes.append(root_node)
        else:
            for child in root_node.children:
                find_max_nodes(child, max_nodes)
    except Exception as e:
        raise e
    finally:
        return max_nodes

def add_children(game_state, current_player):
    """ 
    Given a game state (in the form of a Node object):
        * calculate all possible opponent responses 
        * attach them as children to the provided game state.
    """
    legal_moves = game_state.board.find_legal_moves(current_player)
    for proposed_move in legal_moves:
        # TODO Check to make sure new_board isn't in a final state
        new_board = game_state.board.update(proposed_move.coordinates, current_player, legal_moves)
        game_state.add_child(Node(new_board, parent=game_state, level=game_state.level + 1))

def add_level_to_game_tree(game_tree, current_player):
    """ 
    For all terminal nodes in the game tree:
        * run `add_children` on each. 
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

