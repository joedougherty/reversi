#!/usr/bin/env python
import argparse
from collections import namedtuple
from datetime import datetime
import socket, threading 
import sys

from Game import Game

clients = []
lock = threading.Lock()
games = {}

class gameServer(threading.Thread):
    def __init__(self, (socket,address)):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.COMMANDS = {'games': {'help': 'List games. You can join a game where player_two->None', 'command': self.list_games},
            'help':
                {'help': 'Prints a help message about available commands (including this one!)', 'command': self.help},
            'create':
                {'help': "Create a new game. Usage: 'create <game name>'", 'command': self.create_game},
            'join':
                {'help': "Join a game. Usage: 'join <game name>'", 'command': self.join_game},
            'bail':
                {'help': "Bail on a created game that no one else has joined. :(", 'command': self.bail},
            'name': 
                {'help': "Set your name! Usage: 'name <desired name>'", 'command': self.set_name},
            'whoami':
                {'help': "Learn your current identity!", 'command': self.whoami},
            'players':
                {'help': 'List all the current players on the server.', 'command': self.list_players},
            }
        
        # Flag to maintain whether player is 
        # in a game and expected to propose a move
        self.is_current_player = False

        # Store a ref to the game the player is engaged in
        self.current_game = None
        self.current_game_name = None

        # Set the player name to this anonymous_# thing until they
        # select a more appropriate name for themselves
        self.player_name = 'anonymous_' + str(len(clients) + 1)

    def run(self):
        self.welcome() # Be polite!

        lock.acquire()
        clients.append(self)
        lock.release()

        print("{}:{} connected at {}".format(self.address[0], self.address[1], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        while True:
            data = self.socket.recv(1024)

            if not data:
                break

            self.route_input(data, self)

        self.socket.close()
        print("{}:{} disconnected at {}".format(self.address[0], self.address[1], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        lock.acquire()

        if self.current_game:
            self.clean_up()
        clients.remove(self)
        
        lock.release()

    def welcome(self):
        self.pretty_send("Wilkommen! Use 'help' to list commands.")

    def pretty_send(self, msg, prompt=True):
        """ Add leading and trailing new lines. Fake a command prompt! """
        if msg[-1:] == '\n':
            formatted_msg = "\n{}\n".format(msg)
        else:
            formatted_msg = "\n{}\n\n".format(msg)

        if prompt:
            formatted_msg += "{}@reversi> ".format(self.player_name)
        self.socket.send(formatted_msg)

    def broadcast(self, message):
        for c in clients:
            c.pretty_send(message)

    def run_command(self, data):
        user_command = data.strip().split(' ')
        if user_command[0] not in self.COMMANDS.keys():
            msg = 'Sorry - I do not know how to {}\n'.format(user_command[0])
            msg += "Use 'help' to list commands.\n"
            self.pretty_send(msg)
        else:
            self.COMMANDS.get(user_command[0]).get('command')(user_command[1:])

    def route_input(self, data, reference_to_player):
        """ 
        If the user is playing a game, their input should only be sent
        to that game. 
        
        This prevents users from creating concurrent games, and generally helps
        to avoid some tricky input issues.
        """
        if self.player_is_in_a_game():
            self.current_game.receive_move(data, reference_to_player)
        else:
            self.run_command(data)

    def list_games(self, *args):
        if games == {}:
            self.pretty_send('No games exist yet!')
        else:
            game_list = ''
            for game in games.keys():
                try:
                    player_two = games[game].player_two.player_name
                except:
                    player_two = None
                game_list += "{} :: player_one->{} | player_two->{}\n".format(game, games[game].player_one.player_name, player_two)
            self.pretty_send(game_list)
        
    def help(self, *args):
        all_commands = ''
        for key in self.COMMANDS.keys():
            all_commands += '{}: {}\n'.format(key, self.COMMANDS.get(key).get('help'))
        self.pretty_send(all_commands)

    def create_game(self, args=[], ai=False):
        if args == []:
            self.pretty_send("Please provide a name for the game. Usage: create <game name>")
            return False

        game_name = args[0].strip()

        # User can only create one game at a time!
        if self.current_game: 
            self.pretty_send("You can only create one game at a time!")
            return False

        game = Game(player_one=self, ai=ai)

        # Ensure users can't add a game that already exists (by name) !!
        if games.get(game_name):
            self.pretty_send('A game by that name already exists!')
            return False

        games[game_name] = game

        self.current_game = game
        self.current_game_name = game_name

        msg = "Game '{}' has been created.\n".format(game_name)
        msg += 'Waiting for a second player to join...\n'
        msg += "If you grow impatient waiting, run 'bail'"
        self.pretty_send(msg)

    def join_game(self, args=[]):
        if args == []:
            self.pretty_send("Please name a game to join.")
            return False

        # User can only create one game at a time!
        if self.current_game: 
            self.pretty_send("You need to wait for your first game to start!")
            return False

        game_name = args[0].strip()
        if game_name not in games.keys():
            self.pretty_send("Sorry could not find the game '{}'".format(game_name))
        elif games[game_name].player_two != None:
            # Game already has two players!
            self.pretty_send("Sorry! Game already has two players!")
            return False
        else:
            games[game_name].player_two = self # Set player two
            self.current_game = games[game_name]
            self.current_game_name = game_name
            self.play_game(games[game_name])
        
    def play_game(self, game):
        game.start()

    def player_is_in_a_game(self):
        if self.current_game is not None:
            game_is_active = (self.current_game.player_one is not None and self.current_game.player_two is not None)
            if game_is_active:
                return True
        return False

    def bail(self, *args):
        if games.get(self.current_game_name) is None:
            self.pretty_send("You can't bail! You haven't ever started a game yet!")
            return False

        self.delete_game()
        self.set_current_game_to_none()
        self.pretty_send("You have thusly been set free!")

    def delete_game(self):
        del games[self.current_game_name]

    def set_current_game_to_none(self):
        self.current_game = None
        self.current_game_name = None

    def set_name(self, args=[]):
        if args == []:
            self.pretty_send("Please enter a name!")
            return False
        else:
            self.player_name = """ """.join(args)
            self.pretty_send('Henceforth, you shall be known as: {}'.format(self.player_name))

    def whoami(self, *args):
        self.pretty_send('Your current name is: {}'.format(self.player_name))

    def list_players(self, *args):
        self.pretty_send('\n'.join([x.player_name for x in clients]))

    def alert_opponent_game_is_cancelled(self):
        if self.you_are_player_one() and self.current_game.player_two is not None:
            self.current_game.player_two.pretty_send("Oh no! You're opponent has disconnected. :(")

        if self.you_are_player_two() and self.current_game.player_one is not None:
            self.current_game.player_one.pretty_send("Oh no! You're opponent has disconnected. :(")

    def clean_up(self, *args):
        self.alert_opponent_game_is_cancelled()

        game_to_remove = self.current_game
        current_game_name = self.current_game_name

        for player in (game_to_remove.player_one, game_to_remove.player_two):
            if player:
                player.current_game = None
                player.current_game_name = None

        game_to_remove.player_one = None
        game_to_remove.player_two = None

        del games[current_game_name]

    def you_are_player_one(self):
        return self.current_game and self.current_game.player_one == self

    def you_are_player_two(self):
        return self.current_game and self.current_game.player_two == self

if __name__ == '__main__':
    desc = """ Run a Reversi telnet server! """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-p", "--port", required=False, type=int, help="Port number to run on.", default=1911)
    args = parser.parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', args.port))
    s.listen(4) 

    while True: # wait for socket to connect
        gameServer(s.accept()).start()
