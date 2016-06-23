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
        self.COMMANDS = {'games': {'help': 'List games. You can join a game where player_two->None', 'command': self.list},
            'help':
                {'help': 'Prints a help message about available commands (including this one!)', 'command': self.help},
            'create':
                {'help': "Create a new game. Usage: 'create <game name>", 'command': self.create_game},
            'join':
                {'help': "Join a game. Usage: 'join <game name>'", 'command': self.join_game},
            'bail':
                {'help': "Bail on a created game that no one else has joined. :(", 'command': self.bail},
            'name': 
                {'help': "Set your name! Usage: name <desired name>", 'command': self.set_name},
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

    def list(self, *args):
        if games == {}:
            self.pretty_send('No games exist yet!')
        else:
            for game in games.keys():
                game_list = ''
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

    def create_game(self, args=[]):
        if args == []:
            self.pretty_send("Please provide a name for the game. Usage: create <game name>")
            return False

        game_name = args[0].strip()

        # User can only create one game at a time!
        if self.current_game: 
            self.pretty_send("You can only create one game at a time!")
            return False

        game = Game(player_one=self)

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
            self.play_game(games[game_name])
        
    def play_game(self, game):
        game.start()

    def player_is_in_a_game(self):
        if self.current_game is not None:
            game_is_active = (self.current_game.player_one is not None and self.current_game.player_two is not None)
            if game_is_active:
                return True
        return False

    def remove_finished_game(self):
        del games[self.current_game_name]

    def bail(self, *args):
        if games.get(self.current_game_name) is None:
            self.pretty_send("You can't bail! You haven't ever started a game yet!")
            return False

        del games[self.current_game_name]
        self.current_game = None
        self.current_game_name = None
        self.pretty_send("You have thusly been set free!")

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
        players = ''
        for c in clients:
            players += c.player_name + '\n'

        self.pretty_send(players)

    def quit(self, *args):
        # TODO
        # * remove current player from any existing games
        # * maybe there are other things to clean up? (almost certainly)
        sys.exit(0)

while True: # wait for socket to connect
    gameServer(s.accept(), enable_lock=True).start()
