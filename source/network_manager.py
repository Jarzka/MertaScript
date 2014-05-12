# Thanks to BinaryTides Tutorial for making this all possible. :)
# http://www.binarytides.com/python-socket-programming-tutorial/

# PROTOCOL:
# CON_MSG|Message = A message to displayed on the console
# PLAY_SOUND|fileName = Play a sound file
# TEAM|number = The player says that he is playing on the team number (1 or 2)

import client
import socket
import time
import re
import client_thread
from threading import Thread

class NetworkManager():
    def __init__(self, program):
        self._nextFreeId = 0 # When a new client is connected, assign this value to the client id. Then increment his value.
        self._clients = [] # Array of client objects
        self._BUFFER_SIZE = 65535
        self._socket = None
        self._program = program
        self._isHost = False
        self._running = True # Main loop condition
        
    def get_buffer_size(self):
        return self._BUFFER_SIZE
        
    def start_host(self, port):
        self._isHost = True
        try: 
            print("Server starting...")
            self._socket = socket.socket()
            self._socket.bind(("", port))
            print("Server started.")
            print("Listening at {}".format(self._socket.getsockname()))
            self._socket.listen(5) # The backlog argument specifies the maximum number of queued connections
            # and should be at least 0; the maximum value is system-dependent (usually 5),
            # the minimum value is forced to 0
        except socket.error as e:
            print("Could not start server: {}". format(e))
            return False
        
        while self._running:
            try:
                client_socket, address = self._socket.accept() # Accept a connection.
                # The return value is a pair (conn, address) where conn is a new socket object usable to send and
                # receive data on the connection, and address is the address bound to the socket on the other
                # end of the connection.
                
                print ("Got connection from {}".format(address))
                
                print("Assigning id {} to the client.".format(self._nextFreeId))
                c = client.Client(self._nextFreeId, client_socket) # Create a new client object
                self._nextFreeId += 1
                self._clients.append(c)
                connected_client_thread = client_thread.ClientThread() # Create a new thread that receives messages from the client
                connected_client_thread.init(c, self)
                connected_client_thread.start()
            except socket.error as e:
                print("Error listening client connections: {}".format(e))
                break
        
        print("Server shutting down...")
        self._socket.close()
        
    def disconnect(self):
        self._socket.close()
        self._running = False

    def start_join(self, ip, port):
        while True: # Try to join again if the connection is lost
            print("Connecting to" + ": " + str(ip) + " " + str(port))
            
            try: 
                self._socket = socket.socket()
                self._socket.connect((ip, port))
            except socket.error as e:
                print ("Connection failed: {}". format(e))
                print("Trying again...")
                continue
            
            print ("Connection established: {}".format(self._socket.getsockname()))
            
            # Send team info to the server
            
            time.sleep(1)
            message = "TEAM|" + str(self._program.get_commentator().get_client_team())
            self._socket.sendall(message.encode())
            
            # Listen server messages
            while self._running:
                try:
                    data = self._socket.recv(self._BUFFER_SIZE).decode()
                    # print("Got message from the server: {}".format(data))
                    self._decode_message(data)
                except socket.error as e:
                    print("Error: {}".format(e))
                    break
                
            print("Disconnecting...")
            self._socket.close()
            print("Disconnected. Trying again in a few seconds.")
            time.sleep(2)
            
    def is_host(self):
        return self._isHost

    # @param sender client object who sent the message
    def _decode_message(self, message, sender=None):
        if re.search("^CON_MSG\|.+", message):
            array_message = message.split("|")
            print(array_message[1])
        elif re.search("^PLAY_SOUND\|.+", message):
            array_message = message.split("|")
            self._program.get_commentator().play_file(array_message[1])
            print("Playing sound \"{}\"".format(array_message[1]))
        elif re.search("^TEAM|.+", message):
            array_message = message.split("|")
            if sender is not None:
                print ("Client {} is playing on team {}".format(sender.get_id(), array_message[1]))
                sender.set_team(int(array_message[1]))
            
    def _remove_disconnected_clients(self):
        i = 0
        while i < len(self._clients):
            if not self._clients[i].is_connected():
                self._clients.pop(i)
                i = 0
            i += 1
        
    def send_message_to_all_clients(self, message):
        self._remove_disconnected_clients()
        for client in self._clients:
            print("Sending {} to client {}".format(message, client.get_id()))
            client.get_socket().sendall(message.encode())
    
    # Sends the message to all clients who play in the given team
    def send_message_to_clients(self, message, team):
        self._remove_disconnected_clients()
        for client in self._clients:
            if client.get_team() == team:
                print("Sending {} to client {}".format(message, client.get_id()))
                client.get_socket().sendall(message.encode())