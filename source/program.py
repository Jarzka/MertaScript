# This is the main Program class.
# - Start the Network Manager
# - Constantly read and analyse the game's log file

import re
import time
import commentator
import os.path
import networkmanager
from threading import Thread
    
class Program():
    def __init__(self):
        self._handle_config_file()
        self._readLines = 0 # How many lines have been read from the log file
        self._networkManager = networkmanager.NetworkManager(self)
        self._commentator = commentator.Commentator(self, int(self.get_value_from_config_file("host_round_time")))
        self._readFileIntervalInSeconds = 1 # How often the program scans the log file
        self._running = True # Main loop condition

    # Scans the config file and stores it's values in to variables
    def _handle_config_file(self):
        try:
            self.HOST_PORT = int(self.get_value_from_config_file("host_port"))
            self.JOIN_IP = self.get_value_from_config_file("join_ip")
            self._START_METHOD = self.get_value_from_config_file("start")
            self._PATH_LOGS = self.get_value_from_config_file("host_logs_path")
            self._TEAM_1_PLAYER_NAMES = self._get_team_1_player_names_from_config_file()
            self._CLIENT_TEAM = int(self.get_value_from_config_file("client_team"))
            self._PATH_SOUNDS = "sound\\"
            self._PATH_SOUNDS += self.get_value_from_config_file("sounds_folder")
            self._PATH_SOUNDS += "\\"
            
            # Error checking
            
            # TODO raises an error even if the value is correct. I don't the reason for this.
            #if self._START_METHOD is not "host" and self._START_METHOD is not "join":
            #    raise RuntimeError("config.txt start type should be host or join, but it was" + " " + self._START_METHOD)
            if self._PATH_LOGS[len(self._PATH_LOGS) - 1] is not "\\": # Make sure that the path log ends with a backslash
                self._PATH_LOGS += "\\"
            if self._CLIENT_TEAM is not 1 and self._CLIENT_TEAM is not 2:
                raise RuntimeError("config.txt client_team should be 1 or 2.")
        except BaseException as e:
            print("Error reading the config file: {}".format(e))
    
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
    
    def get_client_team(self):
        return self._CLIENT_TEAM

    def get_enemy_team(self):
        if self._CLIENT_TEAM == 1:
            return 2
        elif self._CLIENT_TEAM == 2:
            return 1
    
    def _get_team_1_player_names_from_config_file(self):
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
        return self._networkManager
    
    def get_path_sounds(self):
        return self._PATH_SOUNDS
    
    def get_commentator(self):
        return self._commentator
    
    # Executes the program
    def exec(self):
        # Host / Join?    
        if self._START_METHOD == "host":
            self._host()
        elif self._START_METHOD == "join":
            self._join()
        
    def _host(self):
        self._start_thread_network_manager("host")
        
        file_name =  self._find_most_recently_edited_log_file()
        while self._running:
            self._read_file(file_name)
            self._commentator.update_state()
            time.sleep(self._readFileIntervalInSeconds)
            
        print("Quitting...")
        self._networkManager.disconnect()
            
    def _join(self):
        self._start_thread_network_manager("join")
        
    # @param method string "host" or "join"
    def _start_thread_network_manager(self, method):
        network_manager_thread = NetworkManagerThread()
        network_manager_thread.init(self, method)
        network_manager_thread.start()
        
    # Finds the file that has been edited most recently (and it's not too old)
    def _find_most_recently_edited_log_file(self):
        print("Finding the most suitable log file...")
        
        most_recently_edited_file_name = None
        most_recently_edited_file_time = 0
        
        while most_recently_edited_file_name is None:
            for fileName in os.listdir(self._PATH_LOGS):
                modification_time = os.path.getmtime(self._PATH_LOGS + fileName)
                if time.time() < modification_time + (60 * 2): # The file has been modified recently
                    if modification_time > most_recently_edited_file_time: # The modification timestamp is newer than the previous one
                        most_recently_edited_file_time = modification_time
                        most_recently_edited_file_name = fileName
                else:
                    print("Found file {}, but it is too old. Searching more...".format(fileName))
            
            # File not found, pause and try again
            time.sleep(2)
            
        print("Found suitable file {}".format(most_recently_edited_file_name))
        return most_recently_edited_file_name

    # Opens the file and processes it. Remembers how many lines have been processed and only affects the new lines
    def _read_file(self, file_name):
        print("{} Reading log file...".format(time.strftime("%H:%M:%S")))
        unread_lines = []
        
        try:
            file = open(self._PATH_LOGS + file_name, "r")
            unread_lines = []
            i = 1
            for line in file:
                if i > self._readLines: # This line has not been read yet
                    unread_lines.append(line)
                    self._readLines += 1
                i += 1
            file.close()
        except BaseException as e:
            print("Error reading the log file: {}".format(e))
        
        for line in unread_lines: # Process the new lines
            # print("{} New line found: {}".format(time.strftime("%H:%M:%S"), line), end="")
            self._scan_line(line)
            
    # This method is used when trying to guess in which team a killer and a victim play
    def _is_team_1_player_the_killer(self, string):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".+killed.+"
        match = re.search(reg_ex, string)
        if match:
            return True
        
        return False
        
    # This method is used when trying to guess in which team a killer and a victim play
    def _is_team_1_player_the_victim(self, string):
        reg_ex = ".+killed.+"
        reg_ex += self._construct_regex_team1()
        match = re.search(reg_ex, string)
        if match:
            return True
        
        return False
    
    # Constructs Regex from team 1 player names in the following format:
    # (player1|player2|player2)
    def _construct_regex_team1(self):
        regEx = "("
        currentName = 1
        for name in self._TEAM_1_PLAYER_NAMES:
            regEx += name
            if currentName is not len(self._TEAM_1_PLAYER_NAMES): # Not the last name
                regEx += "|"
            currentName += 1
        regEx += ")"
        return regEx
    
    # Scans a single line and searches for interesting events
    def _scan_line(self, line):
        # Start from the common ones to save performance
        if self._scan_line_for_team1_teamkiller(line):
            return True
        if self._scan_line_for_team2_teamkiller(line):
            return True
        if self._scan_line_for_team1_kills_enemy_headshot(line):
            return True
        if self._scan_line_for_team2_kills_enemy_headshot(line):
            return True
        if self._scan_line_for_team1_kills_enemy_knife(line):
            return True
        if self._scan_line_for_team2_kills_enemy_knife(line):
            return True
        if self._scan_line_for_round_start(line):
            return True
        if self._scan_line_for_round_end(line):
            return True
        if self._scan_line_for_score_ct(line):
            return True
        if self._scan_line_for_score_t(line):
            return True
        if self._scan_line_for_team1_player_joins_team(line):
            return True
        if self._scan_line_for_setting_round_time(line):
            return True
        if self._scan_line_for_bomb_plant(line):
            return True
        if self._scan_line_for_loading_map(line):
            return True
        if self._scan_line_for_game_end(line):
            return True
        return False

    def _scan_line_for_team1_teamkiller(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".+killed.+"
        reg_ex += self._construct_regex_team1()
        match = re.search(reg_ex, line)
        if match:
            print("Catch: {}".format(line))
            print("Teamkiller in team 1!")
            if self._CLIENT_TEAM == 1:
                self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
            elif self._CLIENT_TEAM == 2:
                self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
                return True
        return False
        
    def _scan_line_for_team2_teamkiller(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed someone who does not play in team 1.
        # However, it is very likely that the player was team 2 player and he killed team 2 player.
        
        reg_ex = ".+killed.+"
        match = re.search(reg_ex, line)
        if match:
            # This is a good match if there is NO team 1 player name BEFORE or AFTER the word killed
            if not self._is_team_1_player_the_killer(match.group(0)) \
            and not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                print("Teamkiller in team 2!")
                if self._CLIENT_TEAM == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
                elif self._CLIENT_TEAM == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
                return True
        return False
                
    def _scan_line_for_team1_kills_enemy_headshot(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".+killed.+"
        reg_ex += "headshot"
        match = re.search(reg_ex, line)
        
        if match:
            if not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                if self._CLIENT_TEAM == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
                elif self._CLIENT_TEAM == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
                return True
        return False
                    
    def _scan_line_for_team2_kills_enemy_headshot(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player. However, it is very likely that the killer was team 2 player.
        
        reg_ex = ".+killed.+"
        reg_ex += self._construct_regex_team1()
        reg_ex += ".+headshot"
        match = re.search(reg_ex, line)
        
        if match:
            if not self._is_team_1_player_the_killer(match.group(0)):
                print("Catch: {}".format(line))
                if self._CLIENT_TEAM == 1: #
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
                elif self._CLIENT_TEAM == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
                return True
        return False
                
    def _scan_line_for_team1_kills_enemy_knife(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".+killed.+"
        reg_ex += "with.+"
        reg_ex += "knife"
        match = re.search(reg_ex, line)
        
        if match:
            if not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                if self._CLIENT_TEAM == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
                elif self._CLIENT_TEAM == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
                return True
        return False
                
    def _scan_line_for_team2_kills_enemy_knife(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player. However, it is very likely that the killer was team 2 player.
        
        reg_ex = ".+killed.+"
        reg_ex += self._construct_regex_team1()
        reg_ex += ".+with.+"
        reg_ex += "knife"
        match = re.search(reg_ex, line)
        
        if match:
            if not self._is_team_1_player_the_killer(match.group(0)):
                print("Catch: {}".format(line))
                if self._CLIENT_TEAM == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
                elif self._CLIENT_TEAM == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
                return True
        return False
                
    def _scan_line_for_round_start(self, line):
        reg_ex = "World triggered.*"
        reg_ex += "Round_Start" # does not include buytime
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            self._commentator.set_round_start_time(int(time.time()))
            
            if self._commentator.get_client_team_points() > self._commentator.get_enemy_team_points():
                    self._commentator.handle_event(self._commentator.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING)
            elif self._commentator.get_client_team_points() < self._commentator.get_enemy_team_points():
                    self._commentator.handle_event(self._commentator.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING)
            return True
        return False
            
    def _scan_line_for_round_end(self, line):
        reg_ex = ".*World triggered.*"
        reg_ex += "Round_End"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            self._commentator.set_round_start_time(0)
            return True
        return False
        
    def _scan_line_for_score_t(self, line):
        # L 08/01/2013 - 23:33:38: Team "TERRORIST" scored "4" with "5" players
        
        reg_ex = "Team.+"
        reg_ex += "\"TERRORIST\".+"
        reg_ex += "scored.+?"
        reg_ex += "\d"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            # We need to get the score points. Do this by selecting the first digit from the match
            match2 = re.search("\d+", match.group(0))
            self._commentator.set_team_points("t", int(match2.group(0)))
            return True
        return False
            
    def _scan_line_for_score_ct(self, line):
        # L 08/01/2013 - 23:33:38: Team "CT" scored "1" with "5" players
        
        reg_ex = "Team.+"
        reg_ex += "\"CT\".+"
        reg_ex += "scored.+?"
        reg_ex += "\d"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            # We need to get the score points. Do this by selecting the first digit from the match
            match2 = re.search("\d+", match.group(0))
            if match2:
                self._commentator.set_team_points("ct", int(match2.group(0)))
                return True
        return False
                
    def _scan_line_for_team1_player_joins_team(self, line):
        # Team 1 player joins T
        reg_ex = self._construct_regex_team1()
        reg_ex += ".+switched from team.+"
        reg_ex += "to.*"
        reg_ex += "<TERRORIST>"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            # We can assume that all team 1 players play on T
            self._commentator.set_team_side(1, "t")
            self._commentator.set_team_side(2, "ct")
            return True
        
        # Team 1 player joins CT
        reg_ex = self._construct_regex_team1()
        reg_ex += ".+switched from team.+"
        reg_ex += "to.*"
        reg_ex += "<CT>"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            # We can assume that all team 1 players play on CT
            self._commentator.set_team_side(1, "ct")
            self._commentator.set_team_side(2, "t")
            return True
        return False
            
    def _scan_line_for_setting_round_time(self, line):
        reg_ex = "mp_roundtime.+?\d"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            # We need to get the value. Do this by selecting the first digit from the match
            match2 = re.search("\d", match.group(0))
            if match2:
                round_time = int(match2.group(0))
                round_time *= 60
                self._commentator.set_round_time(round_time)
                print("Round time changed to {} seconds".format(round_time))
            return True
        return False
                
    def _scan_line_for_bomb_plant(self, line):
        reg_ex = "triggered.+"
        reg_ex += "Planted_The_Bomb"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            if self._commentator.get_team_side(self._CLIENT_TEAM) == "t":
                self._commentator.handle_event(commentator.Commentator.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM)
            return True
        return False
            
    def _scan_line_for_loading_map(self, line):
        reg_ex = "Loading map"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            self._commentator.reset_points()
            return True
        return False
            
    def _scan_line_for_game_end(self, line):
        reg_ex = "Log file closed"
        match = re.search(reg_ex, line)
        
        if match:
            print("Catch: {}".format(line))
            self._running = False
            return True
        return False
        
class NetworkManagerThread(Thread):
    # @param method string "host" or "join"
    def init(self, program, method):
        self._program = program
        self._method = method
    def run(self):
        if self._method == "host":
            self._program.get_network_manager().start_host(self._program.HOST_PORT)
        elif self._method == "join":
            self._program.get_network_manager().start_join(self._program.JOIN_IP, self._program.HOST_PORT)