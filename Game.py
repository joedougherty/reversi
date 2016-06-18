from Board import Board

class Game:
    def __init__(self, player_one, player_two=None, ai=False):
        self.player_one = player_one
        self.player_two = player_two

        self.board = Board()
        
        self.current_player = self.board.BLACK # Black moves first
        self.legal_moves = self.board.find_legal_moves(self.current_player)

        self.proposed_move = False

    def broadcast(self, message):
        for client in (self.player_one.socket, self.player_two.socket):
            client.send(message + '\n')

    def render(self, board_matrix):
        board_rep = ''
        hr = '-------------------------\n'

        board_rep += hr
        for row in board_matrix:
            board_rep += '|' + '|'.join(row) + '|\n'
            board_rep += hr

        return board_rep

    def alternate_player(self):
        pass

    def main(self):
        self.broadcast('So it shall begin!\n')
        self.broadcast(self.render(self.board.matrix))

        """
        while self.legal_moves != []:
            self.broadcast(self.render(self.board.matrix))
            
            # Send this only to the current player
            print("{}: it's your move.".format(current_player))
            print("Your possible moves: {}".format(list(set([x.coordinates for x in legal_moves]))))
            
            while proposed_move not in [x.coordinates for x in legal_moves]:
                proposed_move = validate_proposed_move(input('Propose a move:'))

            board.update(proposed_move, current_player, legal_moves)  
            current_player = alternate_player(current_player)
            legal_moves = board.find_legal_moves(current_player)

        # Broadcast final board and score to both players
        render(board.matrix)
        """
