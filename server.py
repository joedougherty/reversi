import socket, threading
from collections import namedtuple
from Game import Game

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 1911))
s.listen(4) # 4 What?
clients = [] #list of clients connected
lock = threading.Lock()

games = {}

class chatServer(threading.Thread):
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

            self.run_command(data)

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
        # TODO: Ensure users can't add a game that already exists (by name)
        game_name = args[0].strip()

        games[game_name] = game

        self.socket.send("Game '{}' has been created.\n".format(game_name))
        self.socket.send('Wating for a second player to join...\n')

    def join_game(self, args=[]):
        if args == []:
            self.socket.send("Please name a game to join.\n")
            return False

        game_name = args[0].strip()
        if game_name not in games.keys():
            self.socket.send("Sorry could not find the game '{}'\n".format(game_name))
        else:
            games[game_name].player_two = self # Set player two
            self.play_game(games[game_name])
        
    def play_game(self, game):
        game.main()

while True: # wait for socket to connect
    # send socket to chatserver and start monitoring
    chatServer(s.accept(), enable_lock=True).start()
