import socket, threading
from collections import namedtuple

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 1911))
s.listen(4) # 4 What?
clients = [] #list of clients connected
lock = threading.Lock()

### HAHAHA I HAVE NO IDEA WHAT I'M DOING ###
games = [1,2,3]

class chatServer(threading.Thread):
    def __init__(self, (socket,address), enable_lock=True):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.enable_lock = enable_lock
        self.COMMANDS = {'list': 
            {'help': 'List open games.',
             'command': self.list},
            'help':
            {'help': 'Prints a help message about available commands (including this one!)',
             'command': self.help},
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
            if len(user_command) > 1:
                self.COMMANDS.get(user_command[0]).get('command')(user_command[1:])
            else:
                self.COMMANDS.get(user_command[0]).get('command')()

    def list(self):
        for game in games:
            self.socket.send(str(game)+'\n')

    def help(self):
        for key in self.COMMANDS.keys():
            self.socket.send('{}: {}'.format(key, self.COMMANDS.get(key).get('help')) + '\n')


while True: # wait for socket to connect
    # send socket to chatserver and start monitoring
    chatServer(s.accept(), enable_lock=True).start()
