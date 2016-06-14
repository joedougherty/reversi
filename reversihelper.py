def alternate_player(current_player):
    if current_player == board.BLACK:
        return board.WHITE
    return board.BLACK

def render(board_matrix):
    hr = '-------------------------'
    print(hr)
    for row in board_matrix:
        row = '|' + '|'.join(row) + '|'
        print(row)
        print(hr)

def validate_proposed_move(proposed_move):
    try:
        return (int(proposed_move[0]), int(proposed_move[2]))
    except:
        print("Move must be in row,col format. Ex: 5,4") 

