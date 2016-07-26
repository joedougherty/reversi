class Node():
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

def create_tree(root_node, current_player, original_node=None, depth=3):
    # Keep original node around to be returned at the end
    if original_node is None:
        original_node = root_node

    # If we've reached the deepest level and we're on the final board,
    # return the whole damn thing
    if depth == 0:
        return original_node

    legal_moves = root_node.data.find_legal_moves(current_player)
    for proposed_move in legal_moves:
        new_board = board.update(proposed_move.coordinates, current_player, legal_moves)
        root_node.add_child(Node(new_board))

    opponent = alternate_player(current_player)
    
    for new_board in game_tree.children:
        return create_tree(new_board.data, opponent, game_tree, depth=depth-1)

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

root_node = Node(board)

tree = create_tree(root_node, board.BLACK, game_tree=None, depth=3)

