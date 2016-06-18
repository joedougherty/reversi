from Board import Board

class Game:
    def __init__(self, player_one, player_two=None, ai=False):
        self.player_one = player_one
        self.player_two = player_two

        self.board = Board()

        # Default player_one to play black pieces, and thus move first
        self.player_one.color = self.board.BLACK

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

    def alternate_player(self, current_player):
        if current_player == self.player_one:
            return self.player_two
        return self.player_one

    def validate_proposed_move(self, proposed_move):
        try:
            return (int(proposed_move[0]), int(proposed_move[2]))
        except:
            print("Move must be in row,col format. Ex: 5,4") 

    def send(self, player, msg):
        player.socket.send(msg + '\n')

    def receive_move(self, data):
        self.broadcast("I received a move! The move I received was {}".format(data))
        self.received_move = data.strip()

    def check_received_move(self):
        return self.received_move

    def main(self):
        # Don't forget to assign player two their piece color!
        self.player_two.color = self.board.WHITE

        self.broadcast('So it shall begin!\n')

        current_player = self.player_one # Black moves first
        legal_moves = self.board.find_legal_moves(current_player.color)

        proposed_move = False

        while legal_moves != []:

            self.broadcast(self.render(self.board.matrix))
            
            # Send this only to the current player
            self.send(current_player, "{}: it's your move.".format(current_player.color))
            self.send(current_player, "Your possible moves: {}".format(list(set([x.coordinates for x in legal_moves]))))
            
            # TODO
            # Find a while to model the input validation that doesn't 
            # require a while loop

            """
            A while loop doesn't quite make sense here given the distributed, networked nature.

            while proposed_move not in [x.coordinates for x in legal_moves]:
                self.send(current_player, 'Propose a move:')
                proposed_move = self.validate_proposed_move(self.check_received_move())
            """

            self.board.update(proposed_move, current_player, legal_moves)  
            current_player = self.alternate_player(current_player)
            legal_moves = self.board.find_legal_moves(current_player)

        # Broadcast final board and score to both players
        # self.broadcast(self.render(self.board.matrix))
