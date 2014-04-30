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
		self._readLines = 0 # How many lines have been read from the log file (the program processes every line once)
		self._networkManager = networkmanager.NetworkManager(self)
		
		# Load options (these are documented in the readme file)
		
		self._PATH_LOGS = self.get_value_from_config_file("host_logs_path")
		if self._PATH_LOGS[len(self._PATH_LOGS) - 1] is not "\\": # Make sure that the path log ends with a backslash
			self._PATH_LOGS += "\\"
		
		self._TEAM_1_PLAYER_NAMES = self._get_team_1_player_names_from_config_file()
		
		self._CLIENT_TEAM = int(self.get_value_from_config_file("client_team"))
		if self._CLIENT_TEAM > 2:
			self._CLIENT_TEAM = 2
		
		self._PATH_SOUNDS = "sound\\"
		self._PATH_SOUNDS += self.get_value_from_config_file("sounds_folder")
		self._PATH_SOUNDS += "\\"
			
		self._readFileIntervalInSeconds = 1
		self._running = True # Main loop condition
		
		self._speaker = speaker.Speaker(self, int(self.get_value_from_config_file("host_round_time")))
	
	# Looks the key from the config file and returns it's value
	def get_value_from_config_file(self, key):
		file = open("config.txt", "r")
		for line in file:
			if re.search("^" + key, line):
				lineArray = line.split("=")
				lineArray[1] = lineArray[1].strip() # Remove spaces
				result = lineArray[1]
				return result
		return None
	
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
		startMethod = self.get_value_from_config_file("start")
				
		if startMethod == "host" or startMethod == "local":
			self._host()
		elif startMethod == "join":
			self._join()
		
	def _host(self):
		if self.get_value_from_config_file("start") == "host":
			# Start the network manager and run it in it's own thread
			networkManagerThread = NetworkManagerThread()
			networkManagerThread.init(self, "host")
			networkManagerThread.start()
		
		# Start reading the log file forever
		fileName =  self._find_most_recently_edited_log_file()
		while self._running:
			self._read_file(fileName)
			self._speaker.update_state()
			time.sleep(self._readFileIntervalInSeconds)
			
		print("Quitting...")
		self._networkManager.disconnect() # Will also end the server listening thread.
			
	def _join(self):
		# Start the network manager and run it in it's own thread
		networkManagerThread = NetworkManagerThread()
		networkManagerThread.init(self, "join")
		networkManagerThread.start()
		
	def _find_most_recently_edited_log_file(self):
		# Find the file that has been edited most recently (and it's not too old)
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
		
		# Read the file and store unprocessed lines in to array
		fileContent = [] 
		
		try:
			file = open(self._PATH_LOGS + fileName, "r")
			fileContent = [] 
			i = 1
			for line in file:
				if i > self._readLines:
					fileContent.append(line)
					self._readLines += 1
				i += 1
			file.close()
		except BaseException as e:
			print("Error: {}".format(e))
		
		# Process the new lines
		for line in fileContent:
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
	# This method is used when scalling lines
	def _construct_regex_team1(self):
		regEx = "("
		currentName = 1
		for name in self._TEAM_1_PLAYER_NAMES:
			regEx += name
			if currentName is not len(self._TEAM_1_PLAYER_NAMES): # Do we have to add "|" in the end?
				regEx += "|"
			currentName += 1
		regEx += ")"
		return regEx
	
	# Scans a single line and searches for interesting events
	def _scan_line(self, line):
		
		# *************************************************
		# ************** Team 1 teamkiller ****************
		# *************************************************
		
		regEx = self._construct_regex_team1()
		regEx += ".+ killed .+"
		regEx += self._construct_regex_team1()
		match = re.search(regEx, line)
		if match:
			print("Catch: {}".format(line))
			if self._CLIENT_TEAM == 1: # The speacher's comment depends on the player's team
				self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
			elif self._CLIENT_TEAM == 2:
				self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
			return # Match found, we assume that there are not multiple matches in one line
		
		# *************************************************
		# ************** Team 2 teamkiller ****************
		# *************************************************
		
		# Actually the RegEx thinks that someone, who does not play in team 1, killed someone, who does not play in team 1. However, it is very likely that the player was team 2 player and he killed team 2 player.
		
		regEx = ".+ killed .+"
		match = re.search(regEx, line)
		if match:
			# If there is a team 1 player name BEFORE the word killed, this can not be a good match
			# If there is a team 1 player name AFTER the word killed, this can not be a good match
			if not self._is_team_1_player_the_killer(match.group(0)) and not self._is_team_1_player_the_victim(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1: # The speacher's comment depends on the player's team
					self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
				return
		
		# *************************************************
		# ********* Team 1 kills enemy (headshot) *********
		# *************************************************
		
		regEx = self._construct_regex_team1()
		regEx += ".+ killed .+"
		regEx += "headshot"
		match = re.search(regEx, line)
		
		if match:
			# Check that there is NO team 1 player name AFTER the word killed
			if not self._is_team_1_player_the_victim(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1: # The speacher's comment depends on the player's team
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
				return
		
		# *************************************************
		# ********* Team 2 kills enemy (headshot) *********
		# *************************************************
		
		# Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player. However, it is very likely that the killer was team 2 player.
		
		regEx = ".+ killed .+"
		regEx += self._construct_regex_team1()
		regEx += ".+headshot"
		match = re.search(regEx, line)
		
		if match:
			# Check that there is NO team 1 player BEFORE the word killed
			if not self._is_team_1_player_the_killer(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1: # The speacher's comment depends on the player's team
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
				return
		
		# *************************************************
		# ********** Team 1 kills enemy (knife) ***********
		# *************************************************
		
		regEx = self._construct_regex_team1()
		regEx += ".+ killed .+"
		regEx += "with.+"
		regEx += "knife"
		match = re.search(regEx, line)
		
		if match:
			# Check that there is NO team 1 player AFTER the word killed
			if not self._is_team_1_player_the_victim(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1: # The speacher's comment depends on the player's team
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
				return
		
		# *************************************************
		# ********** Team 2 kills enemy (knife) ***********
		# *************************************************
		
		# Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player. However, it is very likely that the killer was team 2 player.
		
		regEx = ".+ killed .+"
		regEx += self._construct_regex_team1()
		regEx += ".+with.+"
		regEx += "knife"
		match = re.search(regEx, line)
		
		if match:
			# Check that there is NO team 1 player BEFORE the word killed
			if not self._is_team_1_player_the_killer(match.group(0)):
				print("Catch: {}".format(line))
				if self._CLIENT_TEAM == 1: # The speacher's comment depends on the player's team
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
				elif self._CLIENT_TEAM == 2:
					self._speaker.say(speaker.Speaker.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
				return
		
		# ***********************************************
		# ****************  Round Start *****************
		# ***********************************************
		
		regEx = ".*World triggered.*"
		regEx += "Round_Start" # does not include buytime)
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._speaker.set_round_start_time(int(time.time()))
			
			if self._speaker.get_client_team_points() > self._speaker.get_enemy_team_points():
					self._speaker.say(self._speaker.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING)
			elif self._speaker.get_client_team_points() < self._speaker.get_enemy_team_points():
					self._speaker.say(self._speaker.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING)
			return
		
		# ***********************************************
		# *****************  Round End ******************
		# ***********************************************
		
		regEx = ".*World triggered.*"
		regEx += "Round_End"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._speaker.set_round_start_time(0)
			return
		
		# ***********************************************
		# ****************** Score **********************
		# ***********************************************
		
		# L 08/01/2013 - 23:33:38: Team "CT" scored "1" with "5" players
		# L 08/01/2013 - 23:33:38: Team "TERRORIST" scored "4" with "5" players
		
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
				return
		
		regEx = "Team.+"
		regEx += "\"TERRORIST\".+" # Actually this matches Team CT too
		regEx += "scored.+?"
		regEx += "\d"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We need to get the score points. Do this by selecting the first digit from the match
			match2 = re.search("\d", match.group(0))
			self._speaker.set_team_points("t", int(match2.group(0)))
			return
		
		# ***********************************************
		# ************ Player plays on team *************
		# ***********************************************
		
		# Just to make sure if the "switched from team" has not been catched.
		# TODO Will be implemented in the future
		
		# ***********************************************
		# ************** Player joins team **************
		# ***********************************************
	
		# Team 1 player joins T
		regEx = self._construct_regex_team1()
		regEx += ".+switched from team.+"
		regEx += "to.*"
		regEx += "<TERRORIST>"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We can assume that all team 1 players plays on T
			self._speaker.set_team_side(1, "t")
			self._speaker.set_team_side(2, "ct")
		
		# Team 1 player joins CT
		regEx = self._construct_regex_team1()
		regEx += ".+switched from team.+"
		regEx += "to.*"
		regEx += "<CT>"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			# We can assume that all team 1 players plays on CT
			self._speaker.set_team_side(1, "ct")
			self._speaker.set_team_side(2, "t")
			return
		
		# ***********************************************
		# ****************** Settings *******************
		# ***********************************************
		
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
				return
			
		# ***********************************************
		# **************** Bomb plant *******************
		# ***********************************************
		
		regEx = "triggered.+"
		regEx += "Planted_The_Bomb"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			if self._speaker.get_team_side(self._CLIENT_TEAM) == "t":
				self._speaker.say(speaker.Speaker.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM)
			return
		
		# ***********************************************
		# ****************** End map ********************
		# ***********************************************
		
		regEx = "Loading map"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._speaker.reset_points();
			return
		
		# ***********************************************
		# ********************* End *********************
		# ***********************************************
		
		regEx = "Log file closed"
		match = re.search(regEx, line)
		
		if match:
			print("Catch: {}".format(line))
			self._running = False
			return
		
class NetworkManagerThread(Thread):
	# @param method string "host" or "join"
	def init(self, program, method):
		self._program = program
		self._method = method
	def run(self):
		if self._method == "host":
			port = int(self._program.get_value_from_config_file("host_port"))
			self._program.get_network_manager().start_host(port)
		elif self._method == "join":
			address = self._program.get_value_from_config_file("join_ip")
			port = int(self._program.get_value_from_config_file("host_port"))
			self._program.get_network_manager().start_join(address, port)