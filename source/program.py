# This is the main Program class.
# - Start the Network Manager
# - Constantly read and analyse the game's log file

import re
import commentator
import network_manager
import log_reader
import network_manager_thread
import time
    
class Program():
    def __init__(self):
        self._START_METHOD = self.get_value_from_config_file("start")
        if not self._START_METHOD == "host" and not self._START_METHOD == "join":
            raise RuntimeError("config.txt start type should be host or join, but it was" + " " + self._START_METHOD)

        self.HOST_PORT = int(self.get_value_from_config_file("host_port"))
        self.JOIN_IP = self.get_value_from_config_file("join_ip")

        self._network_manager = network_manager.NetworkManager(self)
        self._log_reader = log_reader.LogReader(self)
        self._network_manager.set_log_reader(self._log_reader)
        self._commentator = commentator.Commentator(self, self._log_reader)
        self._log_reader.set_commentator(self._commentator)

        self._running = True

    # Executes the program
    def exec(self):
        # Host / Join?
        if self._START_METHOD == "host":
            self._host()
        elif self._START_METHOD == "join":
            self._join()
    
    # Searches the key from the config file and returns it's value
    def get_value_from_config_file(self, key):
        try:
            file = open("config.txt", "r")
            for line in file:
                if re.search("^" + key, line):
                    line_array = line.split("=")
                    line_array[1] = line_array[1].strip() # Remove spaces
                    line_array[1] = line_array[1].strip('\n') # Remove new lines
                    result = line_array[1]
                    return result
            return None
        except BaseException as e:
            print("Error reading the config file: {}".format(e))
    
    def get_team_1_player_names_from_config_file(self):
        file = open("config.txt", "r")
        for line in file:
            if re.search("^host_team_1_player_names", line):
                line_array = line.split("=")
                line_array[1] = line_array[1].replace(" ", "") # Remove spaces
                line_array[1] = line_array[1].strip('\n') # Remove new lines
                result = line_array[1].split(",")
                return result
        return None
    
    def get_network_manager(self):
        return self._network_manager
    
    def get_commentator(self):
        return self._commentator
        
    def _host(self):
        self._start_thread_network_manager("host")

        self._log_reader.initialize()

        while self._running:
            self._log_reader.update_state()
            self._commentator.update_state()
            
        print("Quitting...")
        self._network_manager.disconnect()
            
    def _join(self):
        self._start_thread_network_manager("join")
        
    # @param method string "host" or "join"
    def _start_thread_network_manager(self, method):
        nm_thread = network_manager_thread.NetworkManagerThread()
        nm_thread.init(self, method)
        nm_thread.start()