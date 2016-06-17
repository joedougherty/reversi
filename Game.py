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

    def main(self):
        self.broadcast('So it shall begin!\n')

        """
        while self.legal_moves != []:
            render(board.matrix)
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
