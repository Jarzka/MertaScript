# Thanks to BinaryTides Tutorial for making this all possible. :)
# http://www.binarytides.com/python-socket-programming-tutorial/

# PROTOCOL:

# Messages begin with < and end with >.
# Individual parts (parameters) are separated by |
# First parameter defines the type of the message
#
# From server to client:
# <CON_MSG|Message> = A message to displayed on the console
# <PLAY_SOUND|fileName> = Play a sound file
# <CHECK_FILE|location|SIZE> = Asks if the client has a file in location and it's the given size.
#
# From client to server
# <TEAM|number> = The player says that he is playing on the team number (1 or 2)

import client
import socket
import time
import client_thread
import os
import decode_message_thread


class NetworkManager():
    def __init__(self, program):
        self._nextFreeId = 0 # When a new client is connected, assign this value to the client id. Then increment his value.
        self._clients = [] # Array of client objects
        self._BUFFER_SIZE = 65535
        self._socket = None
        self._program = program
        self._log_reader = None
        self._isHost = False
        self._running = True # Main loop condition

    def set_log_reader(self, log_reader):
        self._log_reader = log_reader
        
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

                 # Create a new thread that receives messages from the client
                connected_client_thread = client_thread.ClientThread()
                connected_client_thread.init(c, self)
                connected_client_thread.start()

                self._send_validate_files(c)
            except socket.error as e:
                print("Error listening client connections: {}".format(e))
                break
        
        print("Server shutting down...")
        self._socket.close()

    def _send_validate_files(self, client):
        search_path = self._log_reader.get_path_sounds()

        try:
            for directory in os.listdir(search_path):
                for file in os.listdir(search_path + directory):
                    if file.endswith(".wav"):
                        message = "<"
                        message += "CHECK_FILE"
                        message += "|"
                        message += search_path + directory + os.path.sep + file
                        message += "|"
                        message += str(os.path.getsize(search_path + directory + os.path.sep + file))
                        message += ">"
                        client.get_socket().sendall(message.encode())
        except FileNotFoundError as e:
            print("Warning: " + e.strerror + ": " + e.filename)
        
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
            message = "<" + "TEAM|" + str(self._program.get_commentator().get_client_team()) + ">"
            self._socket.sendall(message.encode())
            
            # Listen server messages
            server = client.Client(123, self._socket)
            while self._running:
                try:
                    data = self._socket.recv(self._BUFFER_SIZE)
                    # print("Got message from the server: {}".format(data))
                    decode_message = decode_message_thread.DecodeMessageThread()
                    decode_message.init(data, server, self)
                    decode_message.run()
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
    def decode_message(self, message, sender=None):
        try:
            message_decoded = message.decode()
            self._handle_message_utf8(message_decoded, sender)
        except UnicodeDecodeError as e:
            pass

    def _handle_message_utf8(self, message, sender):
        # Split messages and handle them seperately
        for splitted_message in self._split_network_message(message):
            self._handle_message_type_CON_MSG(splitted_message)
            self._handle_message_type_PLAY_SOUND(splitted_message)
            self._handle_message_type_TEAM(splitted_message, sender)
            self._handle_message_type_CHECK_FILE(splitted_message, sender)

    def _split_network_message(self, message):
        messages = message.split(">")

        for index in range(len(messages)):
            messages[index] = messages[index] + ">"

        return messages

    def _handle_message_type_CON_MSG(self, message):
        if message[:9] == "<CON_MSG|":
                array_message = message.split("|")
                print_message = array_message[1][:-1] # Remove last character (>)
                print(print_message)

    def _handle_message_type_PLAY_SOUND(self, message):
        if message[:12] == "<PLAY_SOUND|":
            array_message = message.split("|")
            file_name = array_message[1][:-1] # Remove last character (>)
            self._program.get_commentator().play_file(file_name)
            print("Playing sound \"{}\"".format(file_name))

    def _handle_message_type_TEAM(self, message, sender):
        if message[:6] == "<TEAM|":
            array_message = message.split("|")
            if sender is not None:
                team = array_message[1][:-1] # Remove last character (>)
                print ("Client {} is playing on team {}".format(sender.get_id(), team))
                sender.set_team(int(team))

    def _handle_message_type_CHECK_FILE(self, message, sender):
        if message[:12] == "<CHECK_FILE|":

            try:
                array_message = message.split("|")
                filename = array_message[1]
                if os.path.isfile(filename):
                    pass # TODO CHECK SIZE
                else:
                    print("Warning: missing sound file!")
            except FileNotFoundError as e:
                print("Warning: " + e.strerror + ": " + e.filename)
            
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