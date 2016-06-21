import socket, threading 
from collections import namedtuple
from Game import Game
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 1911))
s.listen(4) # 4 What?
clients = [] #list of clients connected
lock = threading.Lock()

games = {}

class gameServer(threading.Thread):
    def __init__(self, (socket,address), enable_lock=True):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.enable_lock = enable_lock
        self.COMMANDS = {'list': {'help': 'List open games.', 'command': self.list},
            'help':
                {'help': 'Prints a help message about available commands (including this one!)', 'command': self.help},
            'create':
                {'help': 'Create a new game', 'command': self.create_game},
            'join':
                {'help': "Join a game. Usage: 'join <game name>'", 'command': self.join_game},
            }
        
        # Flag to maintain whether player is 
        # in a game and expected to propose a move
        self.is_current_player = False

        # Store a ref to the game the player is engaged in
        self.current_game = None
        self.current_game_name = None

    def run(self):
        self.welcome() # Be polite!

        if self.enable_lock:
            lock.acquire()
        
        clients.append(self)
        
        if self.enable_lock:
            lock.release()

        print '%s:%s connected.' % self.address
        while True:
            data = self.socket.recv(1024)

            if not data:
                break

            self.route_input(data, self)

        self.socket.close()
        print '%s:%s disconnected.' % self.address
        
        if self.enable_lock:
            lock.acquire()

        clients.remove(self)

        if self.enable_lock:
            lock.release()

    def welcome(self):
        msg = "Wilkommen! Use 'help' to list commands.\n"
        self.socket.send(msg)

    def broadcast(self, message):
        for c in clients:
            c.socket.send(message + '\n')

    def run_command(self, data):
        user_command = data.strip().split(' ')
        if user_command[0] not in self.COMMANDS.keys():
            msg = 'Sorry - I do not know how to {}\n'.format(user_command[0])
            msg += "Use 'help' to list commands.\n"
            self.socket.send(msg)
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

    def list(self, *args):
        if games == {}:
            self.socket.send('No games exist yet!\n')
        else:
            for game in games.keys():
                self.socket.send(str(game)+'\n')

    def help(self, *args):
        for key in self.COMMANDS.keys():
            self.socket.send('{}: {}'.format(key, self.COMMANDS.get(key).get('help')) + '\n')

    def create_game(self, args=[]):
        if args == []:
            self.socket.send("Please provide a name for the game.\n")
            return False

        game = Game(player_one=self)
        game_name = args[0].strip()

        # Ensure users can't add a game that already exists (by name) !!
        if games.get(game_name):
            self.socket.send('A game by that name already exists!')
            return False

        games[game_name] = game

        self.current_game = game
        self.current_game_name = game_name

        self.socket.send("Game '{}' has been created.\n".format(game_name))
        self.socket.send('Wating for a second player to join...\n')

    def join_game(self, args=[]):
        if args == []:
            self.socket.send("Please name a game to join.\n")
            return False

        game_name = args[0].strip()
        if game_name not in games.keys():
            self.socket.send("Sorry could not find the game '{}'\n".format(game_name))
        elif games[game_name].player_two != None:
            # Game already has two players!
            self.socket.send("Sorry! Game already has two players!")
            return False
        else:
            games[game_name].player_two = self # Set player two
            self.current_game = games[game_name]
            self.play_game(games[game_name])
        
    def play_game(self, game):
        game.start()

    def player_is_in_a_game(self):
        if self.current_game is not None:
            return True
        return False

    def remove_finished_game(self):
        del games[self.current_game_name]

    def quit(self, *args):
        # TODO
        # * remove current player from any existing games
        # * maybe there are other things to clean up? (almost certainly)
        sys.exit(0)

while True: # wait for socket to connect
    gameServer(s.accept(), enable_lock=True).start()
