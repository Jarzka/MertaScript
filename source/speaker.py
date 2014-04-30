# This is the commentator class.
# - Check that all audio files exist
# - Play audio files
# - Keeps the memory of team points and round time

import winsound
import wave
import contextlib
import time
import random

class Speaker():
	# These constants are used to tell the speacher which type of sound file it's supposed to say
	SOUND_ID_KILL_CLIENT_TEAM = 1 # Not use
	SOUND_ID_KILL_ENEMY_TEAM = 3 # Not use
	SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM = 2 # Client team killed enemy with headshot
	SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM = 4  # Enemy team killed client with headshot
	SOUND_ID_KILL_KNIFE_CLIENT_TEAM = 24 # Client team killed enemy with knife
	SOUND_ID_KILL_KNIFE_ENEMY_TEAM = 25 # Enemy team killed client with knife
	SOUND_ID_TEAMKILLER_CLIENT_TEAM = 5  # There is a teamkiller in client's team
	SOUND_ID_TEAMKILLER_ENEMY_TEAM = 22
	SOUND_ID_SCORE_ENEMY_TEAM = 6 # Enemy team got a point
	SOUND_ID_SCORE_CLIENT_TEAM = 7 # Client team got a point
	SOUND_ID_SCORE_CLIENT_TEAM_3_1 = 8 # Client team got a point and the scores are 3 for client and 1 for enemy
	SOUND_ID_SCORE_CLIENT_TEAM_4_0 = 9 # ...
	SOUND_ID_SCORE_CLIENT_TEAM_5_1 = 10 # ...
	SOUND_ID_SCORE_CLIENT_TEAM_6_1 = 11 # ...
	SOUND_ID_SCORE_CLIENT_TEAM_2_3 = 23 # ...
	SOUND_ID_SCORE_DEFUSE_BOMB_ENEMY_TEAM = 19 # Enemy team got a point by defusing the bomb
	SOUND_ID_TIME_0_10 = 13 # 10 seconds left
	SOUND_ID_TIME_0_30 = 14 # ...
	SOUND_ID_TIME_0_20 = 15 # ...
	SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING = 16 # Round started and the client team has more points
	SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING = 17 # Round started and the enemy team has more points
	SOUND_ID_BOMB_PLANTED_CLIENT_TEAM = 18 # Client's team planted the bomb
	
	# These values present how likely it is that the commentator will say the asked event id
	PROBABILITY_KILL_CLIENT_TEAM = 10 # Not in use
	PROBABILITY_KILL_ENEMY_TEAM = 10 # Not use
	PROBABILITY_KILL_HEADSHOT_CLIENT_TEAM = 100 
	PROBABILITY_KILL_HEADSHOT_ENEMY_TEAM = 100
	PROBABILITY_KILL_KNIFE_CLIENT_TEAM = 100 
	PROBABILITY_KILL_KNIFE_ENEMY_TEAM = 100
	PROBABILITY_TEAMKILLER_CLIENT_TEAM = 100
	PROBABILITY_TEAMKILLER_ENEMY_TEAM = 100
	PROBABILITY_SCORE_ENEMY_TEAM = 100
	PROBABILITY_SCORE_CLIENT_TEAM = 100
	PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC = 100
	PROBABILITY_TIME = 50 # 30
	PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING = 20
	PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING = 100
	PROBABILITY_BOMB_PLANTED_CLIENT_TEAM = 10
	
	def __init__(self, program, roundTime):
		# Attributes
		self._lastTimeStartedSayingInSeconds = 0
		self._lastFileDurationInSeconds = 0
		
		self._roundStartTime = 0 # Unix Timestamp
		self._team1Side = "" # ct or t
		self._team2Side = ""
		self._team1Points = 0
		self._team2Points = 0
		self._roundTimeinSeconds = roundTime
		
		self._program = program
	
		# ID 2
		# The player or a teammate kills somebody with headshot
		self._SOUND_DICTIONARY_KILL_HEADSHOT_CLIENT_TEAM = (
		"taivas_varjele.wav",
		"ai mika laukaus.wav",
		"ja jälleen.wav",
		"aivan mieletön paukku.wav",
		"ja siellä lepää.wav",
		"ilmiömäinen harhautus.wav",
		"ja siellä lepää niin että tärinä kuuluu.wav",
		"aivan mieletön paukku.wav", # REMEMBER TO INSERT COMMA HERE!
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_KILL_HEADSHOT_CLIENT_TEAM)
			
		# ID 4
		# Enemy killed the player or a teammate with headshot
		self._SOUND_DICTIONARY_KILL_HEADSHOT_ENEMY_TEAM = (
		"paha virhe.wav",
		"ja sinne yläkulmaan menee laukaus.wav",
		"se tuli kuin salama kirkkaalta taivaalta.wav",
		"aivan karmaiseva pommi.wav",
		"hirmuinen tälli.wav",
		"olipa tyly.wav",
		"siitä miinus pöytäkirjaan.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_KILL_HEADSHOT_ENEMY_TEAM)
		
		# Kill with knife
		self._SOUND_DICTIONARY_KILL_KNIFE_CLIENT_TEAM = (
		"nostakaa kädes ylös.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_KILL_KNIFE_CLIENT_TEAM)
		
		self._SOUND_DICTIONARY_KILL_KNIFE_ENEMY_TEAM = (
		"ei voi olla totta.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_KILL_KNIFE_ENEMY_TEAM)
		
		# Teamkiller
		self._SOUND_DICTIONARY_TEAMKILLER_CLIENT_TEAM = (
		"herrajestas mitä siellä tapahtui.wav",
		"herranen aika.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_TEAMKILLER_CLIENT_TEAM)

		self._SOUND_DICTIONARY_TEAMKILLER_ENEMY_TEAM = (
		"herrajestas mitä siellä tapahtui.wav",
		"herranen aika.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_TEAMKILLER_ENEMY_TEAM)
		
		# The enemy has defused the bomb
		self._SOUND_DICTIONARY_SCORE_DEFUSE_BOMB_ENEMY_TEAM = (
		"Eihän siitä mitään maalia tule.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_DEFUSE_BOMB_ENEMY_TEAM)
		
		# The enemy team got a score
		self._SOUND_DICTIONARY_SCORE_ENEMY_TEAM = (
		"ei voi oi oi oi.wav",
		"hermo pitää säilyä.wav",
		"oijoijoi virhe.wav",
		"on tämä hirveää.wav",
		"herra paratkoon mikä maali sieltä tulee.wav",
		"aivan hirveää.wav",
		"ja loistava maali ja varmaan näitte millainen hinta siitä jälleen maksettiin.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_ENEMY_TEAM)
		
		# Player's team got a score
		self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM = (
		"aivan loistava maali.wav",
		"pitkä huuto.wav",
		"ja nyyyt on komea maali.wav",
		"aeeee ja sinne menee.wav",
		"se on siinä.wav",
		"sieltä tulee maali.wav",
		"ja sieltä se tulee.wav",
		"laulu raikaa.wav",
		"niin se vain kruunautuu.wav",
		"näittekö minkä maalin kaveri iskee.wav",
		"ja siellä ooon oiii mikä maalii.wav",
		"oiiii joijojijiji.wav",
		"oiiii mikä maali.wav",
		"oijoijoi.wav",
		"oijoijoi2.wav",
		"oijoijoijoi.wav",
		"sinne menee.wav",
		"mikään ei tule enää eteen.wav",
		"hirveetä pökkyä pesään.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM)
		
		# Player's team has 3 points and the enemy team has 1
		self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_3_1 = (
		"3-1.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_3_1)
		
		# Player's team has 4 points and the enemy team has 0
		self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_4_0 = (
		"4-0.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_4_0)
		
		# Player's team has 5 points and the enemy team has 1
		self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_5_1 = (
		"5-1.wav",
		"5-1 2.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_5_1)
			
		# Player's team has 6 points and the enemy team has 1
		self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_6_1 = (
		"6-1.wav",
		)
		
		# Player's team has 6 points and the enemy team has 1
		self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_2_3 = (
		"2-3.wav",
		)
		
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_6_1)

		# 10 seconds left	
		self._SOUND_DICTIONARY_TIME_0_10 = (
		"10 sekuntia.wav",
		"aikaa on vielä.wav",
		"on aikaa vielä.wav",
		"painikaa vääntäkää.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_TIME_0_10)
			
		# 30 seconds left	
		self._SOUND_DICTIONARY_TIME_0_30 = (
		"vajaa puoli minuuttia.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_TIME_0_30)
				
		# 20 seconds left	
		self._SOUND_DICTIONARY_TIME_0_20 = (
		"20 sekuntia.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_TIME_0_20)
		
		# When round star's and player's team is winning
		self._SOUND_DICTIONARY_ROUND_START_CLIENT_TEAM_WINNING = (
		"loppu on enää pelkkää kosmetiikkaa.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_ROUND_START_CLIENT_TEAM_WINNING)
		
		# When round star's and player's team is losing
		self._SOUND_DICTIONARY_ROUND_START_ENEMY_TEAM_WINNING = (
		"no niin sitten on alettava rakentamaan uusia paikkoja.wav",
		"nyt ei saa herpaantua.wav",
		"rauhassa nyt vain oma peli kuntoon.wav",
		"saadaan vaan lisää liikettä niin hyvä tulee.wav",
		"ja nyt taklauksia enemmän.wav",
		"nyt sitten peli käyntiin.wav",
		"tehkää nyt pojat se maali.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_ROUND_START_ENEMY_TEAM_WINNING)
		
		# When player's team plants a bomb
		self._SOUND_DICTIONARY_BOMB_PLANTED_CLIENT_TEAM = (
		"hirmuista painetta.wav",
		)
		
		self._check_dictionary_files(self._SOUND_DICTIONARY_BOMB_PLANTED_CLIENT_TEAM)
		
	def set_round_time(self, timeInSeconds):
		self._roundTimeinSeconds = timeInSeconds
		
	def _check_dictionary_files(self, dictionary):
		i = 0
		while i < len(dictionary):
			file =  dictionary[i]
			try:
				open(self._program.get_path_sounds() + file)
			except:
				print("Warning: file \"{}\" not found from {}".format(file, self._program.get_path_sounds()))
			i += 1 

	# The method randomly chooses a sound file from the given dictionary and returns it.
	# @param dictionary. key = SOUND_ID, value = file.wav
	def _select_sound(self, dictionary):
		if len(dictionary) == 0:
				file = dictionary[0]
				return file
		
		pseudorandomNumber = random.randint(0, len(dictionary) - 1)
		
		# Make sure the number we got is not bigger than len(dictionary)
		while pseudorandomNumber > len(dictionary) - 1:
				pseudorandomNumber /= 2
				pseudorandomNumber /= 3
		
		file = dictionary[pseudorandomNumber]
		print("Choosing sound from the dictionary: {}".format(file))
		return file
	
	def _is_currently_saying_something(self):
		if time.time() > self._lastTimeStartedSayingInSeconds + self._lastFileDurationInSeconds:
			return False
		
		return True
	
	def _probability(self, value):
		value2 = random.randrange(0, 100)
		# print(value2)
		if value >= value2:
			return True
		return False
	
	# This method will ask Network Manager to send a PLAY_SOUND command to all clients
	# @param fileSameTeam string Audio file to be sent for the clients who play in the same team as host
	# @param fileDifferentTeam string Audio file to be sent for the clients who play in different team than host
	def _send_play_sound_command_to_clients(self, fileSameTeam = None, fileDifferentTeam = None):
		if fileSameTeam is not None:
			self._program.get_network_manager().send_message_to_clients_team("PLAY_SOUND|" + fileSameTeam, self._program.get_client_team())
		if fileDifferentTeam is not None:
			self._program.get_network_manager().send_message_to_clients_team("PLAY_SOUND|" + fileDifferentTeam, self._program.get_enemy_team())
	
	# Selects a sound file corresponding to the given eventId. Will also send the play audio command to clients
	# @param probability int How likely is it that the speaker will say the eventId. Procent number between 1 and 100.
	def say(self, eventId):
		# *************** Kills **************
		if (eventId == self.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM):
			if not self._probability(self.PROBABILITY_KILL_HEADSHOT_CLIENT_TEAM):
				return
			
			file = self._select_sound(self._SOUND_DICTIONARY_KILL_HEADSHOT_CLIENT_TEAM) # Randomly select one corresponding sound file
			self.play_file(self._program.get_path_sounds(), file) # Play audio file locally
			
			if self._program.get_network_manager().is_host():
				# Send play audio command for all clients
				# For this type of audio we need to separately select a different audio file for those clients who play on different team than the host
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_KILL_HEADSHOT_ENEMY_TEAM))
				
		elif (eventId == self.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM):
			if not self._probability(self.PROBABILITY_KILL_HEADSHOT_ENEMY_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_KILL_HEADSHOT_ENEMY_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_KILL_HEADSHOT_CLIENT_TEAM))

		elif (eventId == self.SOUND_ID_KILL_KNIFE_CLIENT_TEAM):
			if not self._probability(self.PROBABILITY_KILL_KNIFE_CLIENT_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_KILL_KNIFE_CLIENT_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_KILL_KNIFE_ENEMY_TEAM))
				
		elif (eventId == self.SOUND_ID_KILL_KNIFE_ENEMY_TEAM):
			if not self._probability(self.PROBABILITY_KILL_KNIFE_ENEMY_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_KILL_KNIFE_ENEMY_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_KILL_KNIFE_CLIENT_TEAM))
				
		# *************** Time **************
				
		elif (eventId == self.SOUND_ID_TIME_0_20):
			if not self._probability(self.PROBABILITY_TIME):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_TIME_0_20)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, file)
				
		elif (eventId == self.SOUND_ID_TIME_0_10):
			if not self._probability(self.PROBABILITY_TIME):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_TIME_0_10)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, file)
				
		elif (eventId == self.SOUND_ID_TIME_0_30):
			if not self._probability(self.PROBABILITY_TIME):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_TIME_0_30)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, file)
				
		elif (eventId == self.SOUND_ID_TIME_0_30):
			if not self._probability(self.PROBABILITY_TIME):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_TIME_0_30)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, file)
				
		# *************** Teamkiller **************
				
		elif (eventId == self.SOUND_ID_TEAMKILLER_CLIENT_TEAM):
			if not self._probability(self.PROBABILITY_TEAMKILLER_CLIENT_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_TEAMKILLER_CLIENT_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_TEAMKILLER_ENEMY_TEAM))
				
		elif (eventId == self.SOUND_ID_TEAMKILLER_ENEMY_TEAM):
			if not self._probability(self.PROBABILITY_TEAMKILLER_ENEMY_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_TEAMKILLER_ENEMY_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_TEAMKILLER_CLIENT_TEAM))
				
		# *************** Scores ***************
		
		elif (eventId == self.SOUND_ID_SCORE_CLIENT_TEAM):
			if not self._probability(self.PROBABILITY_SCORE_CLIENT_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_SCORE_ENEMY_TEAM))
				
		elif (eventId == self.SOUND_ID_SCORE_ENEMY_TEAM):
			if not self._probability(self.PROBABILITY_SCORE_ENEMY_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_ENEMY_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM))
		
		elif (eventId == self.SOUND_ID_SCORE_CLIENT_TEAM_2_3):
			if not self._probability(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_2_3)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file)
				
		elif (eventId == self.SOUND_ID_SCORE_CLIENT_TEAM_3_1):
			if not self._probability(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_3_1)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file)
				
		elif (eventId == self.SOUND_ID_SCORE_CLIENT_TEAM_4_0):
			if not self._probability(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_4_0)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file)
				
		elif (eventId == self.SOUND_ID_SCORE_CLIENT_TEAM_5_1):
			if not self._probability(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_5_1)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file)
				
		elif (eventId == self.SOUND_ID_SCORE_CLIENT_TEAM_6_1):
			if not self._probability(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_6_1)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file)
		
		# *************** Round Start ***************
		
		elif (eventId == self.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING):
			if not self._probability(self.PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_ROUND_START_CLIENT_TEAM_WINNING)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_ROUND_START_ENEMY_TEAM_WINNING))
				
		elif (eventId == self.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING):
			if not self._probability(self.PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_ROUND_START_ENEMY_TEAM_WINNING)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file, self._select_sound(self._SOUND_DICTIONARY_ROUND_START_CLIENT_TEAM_WINNING))
				
		# *************** Bomb planted ***************
		
		elif (eventId == self.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM):
			if not self._probability(self.PROBABILITY_BOMB_PLANTED_CLIENT_TEAM):
				return
			file = self._select_sound(self._SOUND_DICTIONARY_BOMB_PLANTED_CLIENT_TEAM)
			self.play_file(self._program.get_path_sounds(), file)
			
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(file)
		
	def play_file(self, path, file):
		filePath = path + file
		if (not self._is_currently_saying_something()):
			self._lastFileDurationInSeconds = self._get_file_duration(filePath)
			self._lastTimeStartedSayingInSeconds = time.time()
			winsound.PlaySound(filePath, winsound.SND_ASYNC)
			
	def _get_file_duration(self, filePath):
		with contextlib.closing(wave.open(filePath,'r')) as f:
			frames = f.getnframes()
			rate = f.getframerate()
			duration = frames / float(rate)
			return duration
		
	def get_client_team_points(self):
		if self._program.get_client_team() == 1:
			return self._team1Points
		
		return self._team2Points
	
	def get_enemy_team_points(self):
		if self._program.get_client_team() == 1:
			return self._team2Points
		
		return self._team1Points
	
	def _get_client_team_side(self):
		if self._program.get_client_team() == 1:
			return self._team1Side
		
		return self._team2Side
		
	# @return Time left in seconds
	def _get_round_time_left(self):
		if self._roundStartTime is not 0:
			return int(self._roundTimeinSeconds -  self._get_match_time_passed())
		return -1
		
	# @return Match time passed in seconds
	def _get_match_time_passed(self):
		if self._roundStartTime is not 0:
			return int(time.time() - self._roundStartTime)
		return -1
	
	def set_round_start_time(self, timeInSeconds):
		self._roundStartTime = timeInSeconds
	
	def reset_points(self):
		print("Reseting team points")
		self._team1Points = 0
		self._team2Points = 0
		
	# 
	def update_state(self):
		self._check_time()
		
	# Checks how much time is left and if it is possible to comment it
	def _check_time(self):
		roundTimeLeft = self._get_round_time_left()
		
		if roundTimeLeft > 0:
			print("Round time left: {}".format(roundTimeLeft))
			
		if roundTimeLeft == 30:
			self.say(self.SOUND_ID_TIME_0_30)
		elif roundTimeLeft == 20:
			self.say(self.SOUND_ID_TIME_0_20)
		elif roundTimeLeft == 10:
			self.say(self.SOUND_ID_TIME_0_10)
		
	# @param teamId int 1 or 2
	def get_points(self, teamId):
		if teamId == 1:
			return self._team1Points
		elif teamId == 2:
			return self._team2Points

	# @param side string ct or t
	def set_team_points(self, side, points):
		# If old points are greater than the new value, then we know that a new match as started
		if self._team1Side == side and points < self._team1Points:
			self.reset_points()
		elif self._team2Side == side and points < self._team2Points:
			self.reset_points()
		
		# Remember values before changing them
		team1PointsOld = self._team1Points
		team2PointsOld = self._team2Points
		clienTeamPointsOld = self.get_client_team_points()
		enemyTeamPointsOld = self.get_enemy_team_points()
		
		print("Team 1 old score {}".format(team1PointsOld))
		print("Team 2 old score {}".format(team2PointsOld))
		
		# Give the points to the team that plays on that side
		if self._team1Side == side:
			print("Team 1 scored {}".format(points))
			self._team1Points = points
		elif self._team2Side == side:
			print("Team 2 scored {}".format(points))
			self._team2Points = points
			
		# Did client team got a new point?
		if self.get_client_team_points() > clienTeamPointsOld:
			print("Client team got more points")
			# Are the points specific?
			if self.get_client_team_points() == 2 and self.get_enemy_team_points() == 3:
				self.say(self.SOUND_ID_SCORE_CLIENT_TEAM_2_3)
			elif self.get_client_team_points() == 3 and self.get_enemy_team_points() == 1:
				self.say(self.SOUND_ID_SCORE_CLIENT_TEAM_3_1)
			elif self.get_client_team_points() == 4 and self.get_enemy_team_points() == 0:
				self.say(self.SOUND_ID_SCORE_CLIENT_TEAM_4_0)
			elif self.get_client_team_points() == 5 and self.get_enemy_team_points() == 1:
				self.say(self.SOUND_ID_SCORE_CLIENT_TEAM_5_1)
			elif self.get_client_team_points() == 6 and self.get_enemy_team_points() == 1:
				self.say(self.SOUND_ID_SCORE_CLIENT_TEAM_6_1)
			else: # No specific score found, play the default sound
				self.say(self.SOUND_ID_SCORE_CLIENT_TEAM)
				
		# Did enemy team got a new point?
		if self.get_enemy_team_points() > enemyTeamPointsOld:
			print("Enemy team got more points")
			self.say(self.SOUND_ID_SCORE_ENEMY_TEAM)

	# Tells in which team the current client is playing
	# @return string ct or t
	def get_team_side(self, teamNumber):
		if teamNumber == 1:
			return self._team1Side
		if teamNumber == 2:
			return self._team2Side

	# @param sode string ct or t
	def set_team_side(self, teamNumber, side):
		if teamNumber == 1:
			self._team1Side = side
		if teamNumber == 2:
			self._team2Side = side
			
		if self._program.get_client_team() == teamNumber:
			print("The client plays now on {} side".format(side))