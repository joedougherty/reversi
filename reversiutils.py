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

def validate_proposed_move(proposed_move):
    try:
        return (int(proposed_move[0]), int(proposed_move[2]))
    except:
        print("Move must be in row,col format. Ex: 5,4") 

