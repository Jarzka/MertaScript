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
	PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING = 10
	PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING = 20
	PROBABILITY_BOMB_PLANTED_CLIENT_TEAM = 5
	
	def __init__(self, program, round_time):
		self._lastTimeStartedSayingInSeconds = 0
		self._lastFileDurationInSeconds = 0
		self._roundStartTime = 0 # Unix Timestamp
		self._team1Side = "" # ct or t
		self._team2Side = ""
		self._team1Points = 0
		self._team2Points = 0
		self._round_time_in_seconds = round_time
		self._program = program
	
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
		
	def set_round_time(self, time_in_seconds):
		self._round_time_in_seconds = time_in_seconds
		
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
	def _select_dictionary_sound_randomly(self, dictionary):
		if len(dictionary) == 0:
				file = dictionary[0]
				return file
		
		pseudo_random_number = random.randint(0, len(dictionary) - 1)
		
		# Make sure the number we got is not bigger than len(dictionary)
		while pseudo_random_number > len(dictionary) - 1:
				pseudo_random_number /= 2
				pseudo_random_number /= 3
		
		file = dictionary[pseudo_random_number]
		print("Choosing sound from the dictionary: {}".format(file))
		return file
	
	def _is_currently_saying_something(self):
		if time.time() > self._lastTimeStartedSayingInSeconds + self._lastFileDurationInSeconds:
			return False
		
		return True
	
	# @param percent int a number between 0 - 100. The higher it is the more likely it is that his function returns True
	def _get_bool_from_percent(self, percent):
		value2 = random.randrange(0, 100)
		# print(value2)
		if percent >= value2:
			return True
		return False
	
	# This method will ask Network Manager to send a PLAY_SOUND command to all clients
	# @param file_Same_team string Audio file name to be sent for the clients who play in the same team as host
	# @param file_different_team string Audio file name to be sent for the clients who play in different team than host
	def _send_play_sound_command_to_clients(self, file_client_team = None, file_enemy_team = None):
		if file_client_team is not None:
			self._program.get_network_manager().send_message_to_clients("PLAY_SOUND|" + file_client_team,
                                                                             self._program.get_client_team())
		if file_enemy_team is not None:
			self._program.get_network_manager().send_message_to_clients("PLAY_SOUND|" + file_enemy_team,
                                                                             self._program.get_enemy_team())
	
	# Play an audio file related to the given eventId. Will also send the play audio command to clients
	def handle_event(self, event_id):
		# The function checks the probability of playing an audio file from a specific dictionary and decides if it is played.
		
		# *************** Kills **************
		if (event_id == self.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM
		and self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_CLIENT_TEAM)):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_HEADSHOT_CLIENT_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_HEADSHOT_ENEMY_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		elif (event_id == self.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM
		and self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_ENEMY_TEAM)):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_HEADSHOT_ENEMY_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_HEADSHOT_CLIENT_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)

		elif (event_id == self.SOUND_ID_KILL_KNIFE_CLIENT_TEAM
		and self._get_bool_from_percent(self.PROBABILITY_KILL_KNIFE_CLIENT_TEAM)):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_KNIFE_CLIENT_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_KNIFE_ENEMY_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		elif (event_id == self.SOUND_ID_KILL_KNIFE_ENEMY_TEAM
		and self._get_bool_from_percent(self.PROBABILITY_KILL_KNIFE_ENEMY_TEAM)):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_KNIFE_ENEMY_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_KILL_KNIFE_CLIENT_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		# *************** Time **************
				
		elif event_id == self.SOUND_ID_TIME_0_20 \
		and self._get_bool_from_percent(self.PROBABILITY_TIME):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TIME_0_20)
			self._handle_event_audio_files(file_client, file_client)
			return True
				
		elif event_id == self.SOUND_ID_TIME_0_10 \
		and self._get_bool_from_percent(self.PROBABILITY_TIME):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TIME_0_10)
			self._handle_event_audio_files(file_client, file_client)
			return True
				
		elif event_id == self.SOUND_ID_TIME_0_30 \
		and self._get_bool_from_percent(self.PROBABILITY_TIME):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TIME_0_30)
			self._handle_event_audio_files(file_client, file_client)
			return True
				
		elif event_id == self.SOUND_ID_TIME_0_30 \
		and self._get_bool_from_percent(self.PROBABILITY_TIME):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TIME_0_30)
			self._handle_event_audio_files(file_client, file_client)
			return True
				
		# *************** Teamkiller **************
				
		elif event_id == self.SOUND_ID_TEAMKILLER_CLIENT_TEAM \
		and self._get_bool_from_percent(self.PROBABILITY_TEAMKILLER_CLIENT_TEAM):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TEAMKILLER_CLIENT_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TEAMKILLER_ENEMY_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		elif event_id == self.SOUND_ID_TEAMKILLER_ENEMY_TEAM \
		and self._get_bool_from_percent(self.PROBABILITY_TEAMKILLER_ENEMY_TEAM):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TEAMKILLER_ENEMY_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_TEAMKILLER_CLIENT_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		# *************** Scores ***************
		
		elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_ENEMY_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		elif event_id == self.SOUND_ID_SCORE_ENEMY_TEAM \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_ENEMY_TEAM):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_ENEMY_TEAM)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
		
		elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_2_3 \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_2_3)
			self._handle_event_audio_files(file_client)
			return True
				
		elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_3_1 \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_3_1)
			self._handle_event_audio_files(file_client)
			return True
				
		elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_4_0 \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_4_0)
			self._handle_event_audio_files(file_client)
			return True
				
		elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_5_1 \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_5_1)
			self._handle_event_audio_files(file_client)
			return True
				
		elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_6_1 \
		and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_SCORE_CLIENT_TEAM_6_1)
			self._handle_event_audio_files(file_client)
			return True
		
		# *************** Round Start ***************
		
		elif event_id == self.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING \
		and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_ROUND_START_CLIENT_TEAM_WINNING)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_ROUND_START_ENEMY_TEAM_WINNING)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		elif event_id == self.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING \
		and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_ROUND_START_ENEMY_TEAM_WINNING)
			file_enemy = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_ROUND_START_CLIENT_TEAM_WINNING)
			self._handle_event_audio_files(file_client, file_enemy)
			return True
				
		# *************** Bomb planted ***************
		
		elif event_id == self.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM \
		and self._get_bool_from_percent(self.PROBABILITY_BOMB_PLANTED_CLIENT_TEAM):
			file_client = self._select_dictionary_sound_randomly(self._SOUND_DICTIONARY_BOMB_PLANTED_CLIENT_TEAM)
			self._handle_event_audio_files(file_client)
			return True
			
		return False
	
	# @param audioFileClient string The file to be played locally and to be send to clients who play in the same team than host
	# @param audioFileEnemy string The file to be sent to client who play in different team than the host
	def _handle_event_audio_files(self, audio_file_client, audio_file_enemy=None):
			self.play_file(self._program.get_path_sounds(), audio_file_client) # Play audio file locally
			if self._program.get_network_manager().is_host():
				self._send_play_sound_command_to_clients(audio_file_client, audio_file_enemy)
		
	def play_file(self, path, file):
		file_path = path + file
		if not self._is_currently_saying_something():
			self._lastFileDurationInSeconds = self._get_file_duration(file_path)
			self._lastTimeStartedSayingInSeconds = time.time()
			winsound.PlaySound(file_path, winsound.SND_ASYNC)
			
	def _get_file_duration(self, file_path):
		with contextlib.closing(wave.open(file_path,'r')) as f:
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
			return int(self._round_time_in_seconds -  self._get_match_time_passed())
		return -1
		
	# @return Match time passed in seconds
	def _get_match_time_passed(self):
		if self._roundStartTime is not 0:
			return int(time.time() - self._roundStartTime)
		return -1
	
	def set_round_start_time(self, time_in_seconds):
		self._roundStartTime = time_in_seconds
	
	def reset_points(self):
		print("Reseting team points")
		self._team1Points = 0
		self._team2Points = 0
		
	def update_state(self):
		self._check_time()
		
	# Checks how much time is left and if it is possible to comment it
	def _check_time(self):
		round_time_left = self._get_round_time_left()
		
		if round_time_left > 0:
			print("Round time left: {}".format(round_time_left))
			
		if round_time_left == 30:
			self.handle_event(self.SOUND_ID_TIME_0_30)
		elif round_time_left == 20:
			self.handle_event(self.SOUND_ID_TIME_0_20)
		elif round_time_left == 10:
			self.handle_event(self.SOUND_ID_TIME_0_10)
		
	# @param teamId int 1 or 2
	def get_points(self, team_id):
		if team_id == 1:
			return self._team1Points
		elif team_id == 2:
			return self._team2Points

	# @param side string ct or t
	def set_team_points(self, side, points):
		# If old points are greater than the new value, then we know that a new match as started
		if self._team1Side == side and points < self._team1Points:
			self.reset_points()
		elif self._team2Side == side and points < self._team2Points:
			self.reset_points()
		
		# Remember old values before changing them
		client_team_points_old = self.get_client_team_points()
		enemy_team_points_old = self.get_enemy_team_points()
		
		# Give the points to the team that plays on that side
		if self._team1Side == side:
			print("Team 1 scored {}".format(points))
			self._team1Points = points
		elif self._team2Side == side:
			print("Team 2 scored {}".format(points))
			self._team2Points = points
			
		# Did client team got a new point?
		if self.get_client_team_points() > client_team_points_old:
			print("Client team got more points")
			# Are the points specific?
			if self.get_client_team_points() == 2 and self.get_enemy_team_points() == 3:
				self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_2_3)
			elif self.get_client_team_points() == 3 and self.get_enemy_team_points() == 1:
				self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_3_1)
			elif self.get_client_team_points() == 4 and self.get_enemy_team_points() == 0:
				self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_4_0)
			elif self.get_client_team_points() == 5 and self.get_enemy_team_points() == 1:
				self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_5_1)
			elif self.get_client_team_points() == 6 and self.get_enemy_team_points() == 1:
				self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_6_1)
			else: # No specific score found, play the default sound
				self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM)
				
		# Did enemy team got a new point?
		if self.get_enemy_team_points() > enemy_team_points_old:
			print("Enemy team got more points")
			self.handle_event(self.SOUND_ID_SCORE_ENEMY_TEAM)

	# Tells in which team the current client is playing
	# @return string ct or t
	def get_team_side(self, team_number):
		if team_number == 1:
			return self._team1Side
		if team_number == 2:
			return self._team2Side

	# @param side string ct or t
	def set_team_side(self, team_number, side):
		if team_number == 1:
			self._team1Side = side
		if team_number == 2:
			self._team2Side = side
			
		if self._program.get_client_team() == team_number:
			print("The client plays now on {} side".format(side))