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
            return False

    def send(self, player, msg):
        player.socket.send(msg + '\n')

    def receive_move(self, data, player_object):
        received_move = data.strip()

        # Is it from the correct player?
        if player_object != self.current_player:
            player_object.socket.send("Hold your horses! It's not your turn yet :)\n")
            return False

        # Is it a valid (syntactically, that is) move?
        proposed_move = self.validate_proposed_move(received_move)
        if not proposed_move:
            self.current_player.socket.send("Move must be in row,col format. Ex: 5,4\n") 
            return False

        # Is it legal?
        legal_moves = self.board.find_legal_moves(self.current_player.color)
        if proposed_move not in [x.coordinates for x in legal_moves]:
            self.current_player.socket.send("Sorry, that's not a legal move.\n")
            return False

        # Update board
        self.board.update(proposed_move, self.current_player.color, legal_moves)  
        self.broadcast(self.render(self.board.matrix))

        # Make sure your opponent still has some possible moves left
        # If so, set the current player to your opponent
        opposing_player = self.alternate_player(self.current_player)
        if self.board.find_legal_moves(self.alternate_player(self.current_player.color)) != []:
            self.current_player = opposing_player

        # Was that the final move?
        if self.this_is_the_final_board():
            self.broadcast("Game over! Here's the score:\n")
            # TODO self.remove players from game
            return False
        else:
            self.send(self.current_player, "{}: it's your move.".format(self.current_player.color))
            legal_moves = self.board.find_legal_moves(self.current_player.color)
            self.send(self.current_player, "Your possible moves: {}".format(list(set([x.coordinates for x in legal_moves]))))
    
    def this_is_the_final_board(self):
        """ If after you move:
                * your opponent has no legal moves
                * you have no legal moves
            then the game is over, even if there are empty spots left.
        """
        opposing_player = self.alternate_player(self.current_player.color)

        if self.board.find_legal_moves(opposing_player) == [] and \
        self.board.find_legal_moves(self.current_player.color) == []:
            return True
        return False

    def main(self):
        # Don't forget to assign player two their piece color!
        self.player_two.color = self.board.WHITE

        self.broadcast('So it shall begin!\n')

        self.current_player = self.player_one # Black moves first

        self.broadcast(self.render(self.board.matrix))
            
        self.send(self.current_player, "{}: it's your move.".format(self.current_player.color))
        legal_moves = self.board.find_legal_moves(self.current_player.color)
        self.send(self.current_player, "Your possible moves: {}".format(list(set([x.coordinates for x in legal_moves]))))
