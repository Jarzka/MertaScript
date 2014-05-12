# This class presents a server client.

class Client():
    def __init__(self, id, socket):
        self._id = id
        self._socket = socket
        self._connected = True
        self._team = 0
        
    def get_id(self):
        return self._id

    def set_send_files_thread(self, send_files_thread):
        self._send_files_thread = send_files_thread
    
    def get_socket(self):
        return self._socket
    
    def is_connected(self):
        return self._connected
    
    def disconnect(self):
        self._connected = False
        self._socket.close()
        
    def get_team(self):
        return self._team
    
    def set_team(self, team):
        self._team = team