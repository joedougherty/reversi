class Node():
    def __init__(self, board, parent=None, level=0):
        self.board = board
        self.children = []
        self.parent = parent
        self.level = level

    def add_child(self, obj):
        self.children.append(obj)

def add_children(root_node, current_player):
    legal_moves = root_node.board.find_legal_moves(current_player)
    for proposed_move in legal_moves:
        # TODO   
        # Check to make sure new_board isn't in a final state
        new_board = board.update(proposed_move.coordinates, current_player, legal_moves)
        root_node.add_child(Node(new_board, parent=root_node, level=root_node.level + 1))

    return root_node

def find_max_nodes(root_node, max_nodes=[], debug=False):
    try:
        if root_node.children == []:
            if debug:
                print(root_node, root_node.level)
            max_nodes.append((root_node, root_node.level))
        else:
            for child in root_node.children:
                find_max_nodes(child, max_nodes)

    except Exception as e:
        raise

    finally:
        return max_nodes

#def expand_full_level(root_node, current_player):
def expand_full_level(root_node, level_to_expand, current_player):
    for child_node in root_node.children:
        add_children(child_node, current_player)

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

root_node = Node(board, parent=None)

tree = add_children(root_node, board.BLACK)

tree.children[0].add_child(Node(board, parent=tree, level=2))

