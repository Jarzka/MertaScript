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
			self._socket.listen(5) # The backlog argument specifies the maximum number of queued connections and should be at least 0; the maximum value is system-dependent (usually 5), the minimum value is forced to 0
		except socket.error as e:
			print("Could not start server: {}". format(e))
			return False
		
		while self._running:
			try:
				clientSocket, address = self._socket.accept() # Accept a connection. The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection, and address is the address bound to the socket on the other end of the connection.
				
				print ("Got connection from {}".format(address))
				
				print("Assigning id {} to the client.".format(self._nextFreeId))
				c = client.Client(self._nextFreeId, clientSocket) # Create a new client object
				self._nextFreeId += 1
				self._clients.append(c)
				clientThread = ClientThread() # Create a new thread that receives messages from the client
				clientThread.init(c, self)
				clientThread.start()
			except socket.error as e:
				print("Error listening client connections: {}".format(e))
				break
		
		print("Server shutting down...")
		self._socket.close()
		
	def disconnect(self):
		self._socket.close()
		self._running = False

	def start_join(self, ip, port):
		while True:
			print("Joining game...")
			
			try: 
				self._socket = socket.socket()
				self._socket.connect((ip, port))
			except socket.error as e:
				print ("Could not join: {}". format(e))
				return False
			
			print ("Host address resolved: {}".format(self._socket.getsockname()))
			
			# Send team info to the server
			
			time.sleep(1)
			message = "TEAM|" + str(self._program.get_client_team())
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
			arrayMessage = message.split("|")
			print(arrayMessage[1])
		elif re.search("^PLAY_SOUND\|.+", message):
			arrayMessage = message.split("|")
			self._program.get_speaker().play_file(self._program.get_path_sounds(), arrayMessage[1])
			print("Playing sound \"{}\"".format(arrayMessage[1]))
		elif re.search("^TEAM|.+", message):
			arrayMessage = message.split("|")
			if sender is not None:
				print ("Client {} is playing on team {}".format(sender.get_id(), arrayMessage[1]))
				sender.set_team(int(arrayMessage[1]))
			
	def _remove_disconnected_clients(self):
		i = 0
		while i < len(self._clients):
			if not self._clients[i].is_connected():
				self._clients.pop(i)
				i = 0
			i += 1
		
	def send_message_to_clients(self, message):
		self._remove_disconnected_clients()
		for client in self._clients:
			print("Sending {} to client {}".format(message, client.get_id()))
			client.get_socket().sendall(message.encode())
	
	# Sends the message to all clients who play in the given team
	def send_message_to_clients_team(self, message, team):
		self._remove_disconnected_clients()
		for client in self._clients:
			if client.get_team() == team:
				print("Sending {} to client {}".format(message, client.get_id()))
				client.get_socket().sendall(message.encode())

class ClientThread(Thread):
	def init(self, client, networkManager):
		self._client = client
		self._networkManager = networkManager
		
	def run(self):
		# In python 3, bytes strings and unicode strings are now two different types. Since sockets are not aware of string encodings, they are using raw bytes strings, that have a slightly different interface from unicode strings. So, now, whenever you have a unicode string that you need to use as a byte string, you need to encode() it. And when you have a byte string, you need to decode it to use it as a regular (python 2.x) string. Unicode strings are quotes enclosed strings. Bytes strings are b"" enclosed strings
		self._client.get_socket().sendall("CON_MSG|Welcome to the server.".encode()) # Function sendall will simply send data.

		while True:
			try:
				data = self._client.get_socket().recv(self._networkManager.get_buffer_size()).decode()
				# print("Got message from client id {}: {}".format(self._client.get_id(), data))
				self._networkManager._decode_message(data, self._client)
			except:
				print("Client {} disconnected".format(self._client.get_id()))
				break

		self._client.disconnect() # Set client status disconnected