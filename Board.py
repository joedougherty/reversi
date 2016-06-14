# -*- coding: utf-8 -*-

from collections import namedtuple
from directions import north, east, south, west, \
                    northeast, northwest, southeast, southwest

legalmove = namedtuple('legalmove', ['coordinates', 'direction', 'origin'])

class Board:
    def __init__(self):
        self.BLACK = '○ '
        self.WHITE = '● '
        self.EMPTY = '  '

        self.allowedvalues = (self.BLACK, self.WHITE, self.EMPTY)

        self.matrix = []
        for i in range(0,8):
            self.matrix.append([self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, 
                                self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY])
    
        # Set up starting board
        self.matrix[3][3] = self.WHITE
        self.matrix[3][4] = self.BLACK
        self.matrix[4][3] = self.BLACK
        self.matrix[4][4] = self.WHITE

    def find_pieces(self, color):
        found_pieces = []
        for vidx, row in enumerate(self.matrix):
            for hidx, col in enumerate(row):
                if col == color:
                    found_pieces.append((vidx,hidx))   

        return found_pieces

    def reveal(self, position):
        return self.matrix[position[0]][position[1]]

    def opposing_color(self, current_color):
        if current_color == self.BLACK:
            return self.WHITE
        return self.BLACK

    def is_empty(self, position):
        try:
            return self.matrix[position[0]][position[1]] == self.EMPTY
        except IndexError:
            print('** DEBUG ** position passed in was: {}'.format(position))

    def is_out_of_bounds(self, position):
        return position[0] < 0 or position[1] < 0 or position[0] > 7 or position[1] > 7

    def is_on_perimeter(self, position):
        perimeter_values = (0,7)
        return position[0] in perimeter_values or position[1] in perimeter_values

    def check_legality(self, position, current_player, direction):
        next_spot = direction(position)

        if self.is_out_of_bounds(next_spot):
            return False
        elif self.is_empty(next_spot):
            return False
        elif self.reveal(next_spot) == current_player:
            return False
        elif (self.reveal(next_spot) == self.opposing_color(current_player) 
            and not self.is_out_of_bounds(direction(next_spot))
            and self.is_empty(direction(next_spot))):
            # If next spot is the opposing color and the spot beyond that is empty
            return legalmove(direction(next_spot), direction, position)
        elif self.reveal(next_spot) == self.opposing_color(current_player):
            return self.check_legality(next_spot, current_player, direction)
        else:
            raise Exception('Edge case encountered! Original position was: {} and direction was {}'.format(position, direction.func_name)) 

    def find_legal_moves(self, current_player):
        """ Search all eight directions. """
        legal_moves = [] 
        found_pieces = self.find_pieces(current_player)
        for spot in found_pieces:
            for direction in (north, south, east, west, northeast, southeast, northwest, southwest):
                legal = self.check_legality(spot, current_player, direction)
                if legal != False:
                    legal_moves.append(legal)

        return legal_moves

    def set_spot(self, position, color_to_set):
        self.matrix[position[0]][position[1]] = color_to_set

    def update(self, spot_to_claim, color_to_set, legal_moves):
        self.set_spot(spot_to_claim, color_to_set) 
        for move in [x for x in legal_moves if x.coordinates == spot_to_claim]:
            spot = move.origin
            while spot != spot_to_claim:
                self.set_spot(spot, color_to_set)
                spot = move.direction(spot)

    def count_pieces(self, color):
        count = 0
        for row in self.matrix:
            for col in row:
                if col == color:
                    count = count + 1

        return count

    def dump_machine_representation(self):
        print(self.matrix)
