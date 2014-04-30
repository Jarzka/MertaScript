# This is the main Program class.
# - Start the Network Manager
# - Constantly read and analyse the game's log file

import re
import time
import speaker
import os.path
import networkmanager
from threading import Thread
	
class Program():
	def __init__(self):
		self._handle_config_file()
		self._readLines = 0 # How many lines have been read from the log file
		self._networkManager = networkmanager.NetworkManager(self)
		self._speaker = speaker.Speaker(self, int(self.get_value_from_config_file("host_round_time")))
		self._readFileIntervalInSeconds = 1 # How often the program scans the log file
		self._running = True # Main loop condition

	# Scans the config file and stores it's values in to variables
	def _handle_config_file(self):
		try:
			self._HOST_PORT = int(self._program.get_value_from_config_file("host_port"))
			self._JOIN_IP = self._program.get_value_from_config_file("join_ip")
			self._START_METHOD = self.get_value_from_config_file("start")
			self._PATH_LOGS = self.get_value_from_config_file("host_logs_path")
			self._TEAM_1_PLAYER_NAMES = self._get_team_1_player_names_from_config_file()
			self._CLIENT_TEAM = int(self.get_value_from_config_file("client_team"))
			self._PATH_SOUNDS = "sound\\"
			self._PATH_SOUNDS += self.get_value_from_config_file("sounds_folder")
			self._PATH_SOUNDS += "\\"
			
			# Error checking
			if self._START_METHOD is not "host" and self._START_METHOD is not "join":
				raise RuntimeError("config.txt start type should be host or join.")
			if self._PATH_LOGS[len(self._PATH_LOGS) - 1] is not "\\": # Make sure that the path log ends with a backslash
				self._PATH_LOGS += "\\"
			if self._CLIENT_TEAM is not 1 and self._CLIENT_TEAM is not 2:
				raise RuntimeError("config.txt client_team should be 1 or 2.")
		except BaseException as e:
			print("Error reading the config file: {}".format(e))
	
	# Looks the key from the config file and returns it's value
	def get_value_from_config_file(self, key):
		try:
			file = open("config.txt", "r")
			for line in file:
				if re.search("^" + key, line):
					lineArray = line.split("=")
					lineArray[1] = lineArray[1].strip() # Remove spaces
					result = lineArray[1]
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
				lineArray = line.split("=")
				lineArray[1] = lineArray[1].replace(" ", "")
				result = lineArray[1].split(",")
				return result
		return None
	
	def get_network_manager(self):
		return self._networkManager
	
	def get_path_sounds(self):
		return self._PATH_SOUNDS
	
	def get_speaker(self):
		return self._speaker
	
	# Executes the program
	def exec(self):
		# Host / Join?	
		if self._START_METHOD == "host":
			self._host()
		elif startMethod == "join":
			self._join()
		
	def _host(self):
		self._start_thread_network_manager("host")
		
		fileName =  self._find_most_recently_edited_log_file()
		while self._running:
			self._read_file(fileName)
			self._speaker.update_state()
			time.sleep(self._readFileIntervalInSeconds)
			
		print("Quitting...")
		self._networkManager.disconnect()
			
	def _join(self):
		self._start_thread_network_manager("join")
		
	# @param method string "host" or "join"
	def _start_thread_network_manager(self, method):
		networkManagerThread = NetworkManagerThread()
		networkManagerThread.init(self, method)
		networkManagerThread.start()
		
	# Finds the file that has been edited most recently (and it's not too old)
	def _find_most_recently_edited_log_file(self):
		print("Finding the most suitable log file...")
		
		mostRecentlyEditedFileName = None
		mostRecentlyEditedfileTime = 0
		
		while mostRecentlyEditedFileName is None:
			for fileName in os.listdir(self._PATH_LOGS):
				modificationTime = os.path.getmtime(self._PATH_LOGS + fileName)
				if time.time() < modificationTime + (60 * 2): # The file has been modified recently
					if modificationTime > mostRecentlyEditedfileTime: # The modification timestamp is newer than the previous one
						mostRecentlyEditedfileTime = modificationTime
						mostRecentlyEditedFileName = fileName
				else:
					print("Found file {}, but it is too old. Searching more...".format(fileName))
			
			# File not found, pause and try again
			time.sleep(2)
			
		print("Found suitable file {}".format(mostRecentlyEditedFileName))
		return mostRecentlyEditedFileName

	# Opens the file and processes it. Remembers how many lines have been processed and only affects the new lines
	def _read_file(self, fileName):
		print("{} Reading log file...".format(time.strftime("%H:%M:%S")))
		unreadLines = [] 
		
		try:
			file = open(self._PATH_LOGS + fileName, "r")
			unreadLines = [] 
			i = 1
			for line in file:
				if i > self._readLines: # This line has not been read yet
					unreadLines.append(line)
					self._readLines += 1
				i += 1
			file.close()
		except BaseException as e:
			print("Error reading the log file: {}".format(e))
		
		for line in unreadLines: # Process the new lines
			# print("{} New line found: {}".format(time.strftime("%H:%M:%S"), line), end="")
			self._scan_line(line)
			
	# This method is used when trying to guess in which team a killer and a victim play
	def _is_team_1_player_the_killer(self, string):
		regEx = self._construct_regex_team1()
		regEx += ".+ killed "
		match = re.search(regEx, string)
		if match:
			return True
		
		return False
		
	# This method is used when trying to guess in which team a killer and a victim play
	def _is_team_1_player_the_victim(self, string):
		regEx = " killed .+"
		regEx += self._construct_regex_team1()
		match = re.search(regEx, string)
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
		if self._scan_line_for_team2_teamkiller(line):
			return True
		if self._scan_line_for_team1_teamkiller(line):
			return True
		if self._scan_line_for_team1_kills_enemy_headshot(line):
			return True
		if self._scan_line_for_team1_kills_enemy_knife(line):
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
		
	def _scan_line_for_team2_teamkiller(self, line):
		# Actually the RegEx thinks that someone, who does not play in team 1, killed someone who does not play in team 1.
		# However, it is very likely that the player was team 2 player and he killed team 2 player.
		
		regEx = ".+ killed .+"
		match = re.search(regEx, line)
		if match:
			# This is a good match if there is NO team 1 player name BEFORE or AFTER the word killed
			if not self._is_team_1_player_the_killer(match.group(0)) \
			and not self._is_team_1_player_the_victim(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1:
					self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
				return True
		return False
			
	def _scan_line_for_team1_teamkiller(self, line):	
		regEx = self._construct_regex_team1()
		regEx += ".+ killed .+"
		regEx += self._construct_regex_team1()
		match = re.search(regEx, line)
		if match:
			print("Catch: {}".format(line))
			if self._CLIENT_TEAM == 1:
				self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
			elif self._CLIENT_TEAM == 2:
				self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
				return True
		return False
				
	def _scan_line_for_team1_kills_enemy_headshot(self, line):
		regEx = self._construct_regex_team1()
		regEx += ".+ killed .+"
		regEx += "headshot"
		match = re.search(regEx, line)
		
		if match:
			if not self._is_team_1_player_the_victim(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
				return True
		return False
					
	def _scan_line_for_team2_kills_enemy_headshot(self, line):
		# Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player. However, it is very likely that the killer was team 2 player.
		
		regEx = ".+ killed .+"
		regEx += self._construct_regex_team1()
		regEx += ".+headshot"
		match = re.search(regEx, line)
		
		if match:
			if not self._is_team_1_player_the_killer(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1: #
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
				return True
		return False
				
	def _scan_line_for_team1_kills_enemy_knife(self, line):
		regEx = self._construct_regex_team1()
		regEx += ".+ killed .+"
		regEx += "with.+"
		regEx += "knife"
		match = re.search(regEx, line)
		
		if match:
			if not self._is_team_1_player_the_victim(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
				return True
		return False
				
	def _scan_line_for_team2_kills_enemy_knife(self, line):
		# Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player. However, it is very likely that the killer was team 2 player.
		
		regEx = ".+ killed .+"
		regEx += self._construct_regex_team1()
		regEx += ".+with.+"
		regEx += "knife"
		match = re.search(regEx, line)
		
		if match:
			if not self._is_team_1_player_the_killer(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
				return True
		return False
				
	def _scan_line_for_round_start(self, line):
		regEx = ".*World triggered.*"
		regEx += "Round_Start" # does not include buytime
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._speaker.set_round_start_time(int(time.time()))
			
			if self._speaker.get_client_team_points() > self._speaker.get_enemy_team_points():
					self._speaker.say(self._speaker.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING)
			elif self._speaker.get_client_team_points() < self._speaker.get_enemy_team_points():
					self._speaker.say(self._speaker.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING)
			return True
		return False
			
	def _scan_line_for_round_end(self, line):
		regEx = ".*World triggered.*"
		regEx += "Round_End"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._speaker.set_round_start_time(0)
			return True
		return False
		
	def _scan_line_for_score_t(self, line):
		# L 08/01/2013 - 23:33:38: Team "TERRORIST" scored "4" with "5" players
		
		regEx = "Team.+"
		regEx += "\"TERRORIST\".+"
		regEx += "scored.+?"
		regEx += "\d"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We need to get the score points. Do this by selecting the first digit from the match
			match2 = re.search("\d", match.group(0))
			self._speaker.set_team_points("t", int(match2.group(0)))
			return True
		return False
			
	def _scan_line_for_score_ct(self, line):
		# L 08/01/2013 - 23:33:38: Team "CT" scored "1" with "5" players
		
		regEx = "Team.+"
		regEx += "\"CT\".+"
		regEx += "scored.+?"
		regEx += "\d"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We need to get the score points. Do this by selecting the first digit from the match
			match2 = re.search("\d", match.group(0))
			if (match2):
				self._speaker.set_team_points("ct", int(match2.group(0)))
				return True
		return False
				
	def _scan_line_for_team1_player_joins_team(self, line):
		# Team 1 player joins T
		regEx = self._construct_regex_team1()
		regEx += ".+switched from team.+"
		regEx += "to.*"
		regEx += "<TERRORIST>"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We can assume that all team 1 players play on T
			self._speaker.set_team_side(1, "t")
			self._speaker.set_team_side(2, "ct")
			return True
		
		# Team 1 player joins CT
		regEx = self._construct_regex_team1()
		regEx += ".+switched from team.+"
		regEx += "to.*"
		regEx += "<CT>"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We can assume that all team 1 players play on CT
			self._speaker.set_team_side(1, "ct")
			self._speaker.set_team_side(2, "t")
			return True
		return False
			
	def _scan_line_for_setting_round_time(self, line):
		regEx = "mp_roundtime.+?\d"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We need to get the value. Do this by selecting the first digit from the match
			match2 = re.search("\d", match.group(0))
			if (match2):
				roundTime = int(match2.group(0))
				roundTime *= 60
				self._speaker.set_round_time(roundTime)
				print("Round time changed to {} seconds".format(roundTime))
			return True
		return False
				
	def _scan_line_for_bomb_plant(self, line):
		regEx = "triggered.+"
		regEx += "Planted_The_Bomb"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			if self._speaker.get_team_side(self._CLIENT_TEAM) == "t":
				self._speaker.say(speaker.Speaker.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM)
			return True
		return False
			
	def _scan_line_for_loading_map(self, line):
		regEx = "Loading map"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._speaker.reset_points();
			return True
		return False
			
	def _scan_line_for_game_end(self, line):
		regEx = "Log file closed"
		match = re.search(regEx, line)
		
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
			self._program.get_network_manager().start_host(self._HOST_PORT)
		elif self._method == "join":
			self._program.get_network_manager().start_join(self._JOIN_IP, self._HOST_PORT)