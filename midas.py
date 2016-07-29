class Node():
    def __init__(self, board, parent=None, level=0):
        self.board = board
        self.children = []
        self.parent = parent
        self.level = level

    def add_child(self, obj):
        self.children.append(obj)

def find_max_nodes(root_node, max_nodes=None):
    try:
        if max_nodes is None:
            max_nodes = []

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
    legal_moves = game_state.board.find_legal_moves(current_player)
    for proposed_move in legal_moves:
        # TODO Check to make sure new_board isn't in a final state
        new_board = game_state.board.update(proposed_move.coordinates, current_player, legal_moves)
        game_state.add_child(Node(new_board, parent=game_state, level=game_state.level + 1))

def add_level_to_game_tree(game_tree, current_player):
    for terminal_node in find_max_nodes(game_tree):
        add_children(terminal_node, current_player)
    return game_tree

def add_turns(root_node, current_player, num_of_turns=1):
    while num_of_turns > 0:
        add_level_to_game_tree(root_node, current_player)
        add_level_to_game_tree(root_node, alternate_player(current_player))
        num_of_turns = num_of_turns - 1
    return root_node

def alternate_player(current_player):
    if current_player == board.BLACK:
        return board.WHITE
    return board.BLACK

def render(board_matrix):
    board_rep = ''
    pos_hdr = ' '
    for pos in range(len(board_matrix)):
        pos_hdr += '| {}'.format(pos)
        
    hr = '--------------------------\n'

    board_rep += pos_hdr + '|\n' + hr
    for pos, row in enumerate(board_matrix):
        board_rep += '{}|'.format(pos) + '|'.join(row) + '|\n'
        board_rep += hr

    print(board_rep)

from Board import Board
board = Board()
