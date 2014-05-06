# This is the commentator class.
# - Check that all audio files exist
# - Play audio files
# - Knows team points and round time

import winsound
import wave
import contextlib
import time
import random
import os

class Commentator():
    # These constants are used to tell the commentator which type of sound file it's supposed to say
    SOUND_ID_KILL_CLIENT_TEAM = 1 # Not used atm
    SOUND_ID_KILL_ENEMY_TEAM = 3
    SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM = 2 # Client team killed an enemy with headshot
    SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM = 4  # Enemy team killed an client with headshot
    SOUND_ID_KILL_KNIFE_CLIENT_TEAM = 24 # Client team killed an enemy with knife
    SOUND_ID_KILL_KNIFE_ENEMY_TEAM = 25 # Enemy team killed an client with knife
    SOUND_ID_KILL_HEGRENADE_CLIENT_TEAM = 2224 # Client team killed an enemy with hegrenade
    SOUND_ID_KILL_HEGRENADE_ENEMY_TEAM = 26775 # Enemy team killed an client with hegrenade
    SOUND_ID_KILL_INFERNO_CLIENT_TEAM = 2545 # Client team killed an enemy with inferno
    SOUND_ID_KILL_INFERNO_ENEMY_TEAM = 455 # Enemy team killed an client with inferno
    SOUND_ID_TEAMKILLER_CLIENT_TEAM = 5  # There is a teamkiller in client's team
    SOUND_ID_TEAMKILLER_ENEMY_TEAM = 22
    SOUND_ID_SUICIDE = 13438 # Somebody committed a suicide
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
    SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING_MASSIVELY = 16344
    SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING = 17 # Round started and the enemy team has more points
    SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING_MASSIVELY = 1754
    SOUND_ID_BOMB_PLANTED_CLIENT_TEAM = 18 # Client's team planted the bomb
    
    # These values present how likely it is that the commentator will say the asked event id
    PROBABILITY_KILL_CLIENT_TEAM = 10 # Not used atm
    PROBABILITY_KILL_ENEMY_TEAM = 10
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
    PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING_MASSIVELY = 50
    PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING = 20
    PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING_MASSIVELY = 50
    PROBABILITY_BOMB_PLANTED_CLIENT_TEAM = 5
    
    def __init__(self, program, round_time, max_rounds):
        self._started_saying_something_timestamp_in_seconds = 0
        self._last_file_duration_in_seconds = 0
        self._round_start_timestamp_in_seconds = 0
        self._team1_side = "" # ct or t
        self._team2_side = ""
        self._team1_points = 0
        self._team2_points = 0
        self._round_time_in_seconds = round_time
        self._max_rounds = max_rounds
        self._program = program
    
        self._initialize_dictionaries()
        
        self._check_dictionary_files(self._sound_dictionary_bomb_planted_client_team)
        
    def _initialize_dictionaries(self):
        self._sound_dictionary_kill_headshot_client_team = self._load_sound_files("kill-headshot-client")
        self._sound_dictionary_kill_headshot_enemy_team = self._load_sound_files("kill-headshot-enemy")

        self._sound_dictionary_kill_knife_client_team = self._load_sound_files("kill-knife-client")
        self._sound_dictionary_kill_knife_enemy_team = self._load_sound_files("kill-knife-enemy")
        self._sound_dictionary_kill_hegrenade_client_team = self._load_sound_files("kill-hegrenade-client")
        self._sound_dictionary_kill_hegrenade_enemy_team = self._load_sound_files("kill-hegrenade-enemy")
        self._sound_dictionary_kill_inferno_client_team = self._load_sound_files("kill-inferno-client")
        self._sound_dictionary_kill_inferno_enemy_team = self._load_sound_files("kill-inferno-enemy")

        self._sound_dictionary_teamkiller_client_team = self._load_sound_files("teamkiller-client")
        self._sound_dictionary_teamkiller_enemy_team = self._load_sound_files("teamkiller-enemy")

        self._sound_dictionary_score_client_team = self._load_sound_files("score-client")
        self._sound_dictionary_score_client_team_1_0 = self._load_sound_files("score-client-1-0")
        self._sound_dictionary_score_client_team_1_1 = self._load_sound_files("score-client-1-1")
        self._sound_dictionary_score_client_team_2_0 = self._load_sound_files("score-client-2-0")
        self._sound_dictionary_score_client_team_2_1 = self._load_sound_files("score-client-2-1")
        self._sound_dictionary_score_client_team_2_2 = self._load_sound_files("score-client-2-2")
        self._sound_dictionary_score_client_team_2_3 = self._load_sound_files("score-client-2-3")
        self._sound_dictionary_score_client_team_3_0 = self._load_sound_files("score-client-3-0")
        self._sound_dictionary_score_client_team_3_1 = self._load_sound_files("score-client-3-1")
        self._sound_dictionary_score_client_team_3_2 = self._load_sound_files("score-client-3-2")
        self._sound_dictionary_score_client_team_4_0 = self._load_sound_files("score-client-4-0")
        self._sound_dictionary_score_client_team_5_1 = self._load_sound_files("score-client-5-1")
        self._sound_dictionary_score_client_team_6_1 = self._load_sound_files("score-client-6-1")
        self._sound_dictionary_score_even_client_team = self._load_sound_files("score-even-client")
        self._sound_dictionary_score_enemy_team = self._load_sound_files("score-enemy")
        self._sound_dictionary_score_win_client_team = self._load_sound_files("score-win-client")
        self._sound_dictionary_score_win_enemy_team = self._load_sound_files("score-win-enemy")

        self._sound_dictionary_suicide = self._load_sound_files("suicide")

        self._sound_dictionary_time_0_03 = self._load_sound_files("time-0-03")
        self._sound_dictionary_time_0_10 = self._load_sound_files("time-0-10")
        self._sound_dictionary_time_0_15 = self._load_sound_files("time-0-15")
        self._sound_dictionary_time_0_20 = self._load_sound_files("time-0-20")
        self._sound_dictionary_time_0_30 = self._load_sound_files("time-0-30")
        self._sound_dictionary_time_0_40 = self._load_sound_files("time-0-40")
        self._sound_dictionary_time_1_00 = self._load_sound_files("time-1-00")

        self._sound_dictionary_round_start_client_team_winning = self._load_sound_files("round-start-client-winning")
        self._sound_dictionary_round_start_enemy_team_winning = self._load_sound_files("round-start-enemy-winning")
        self._sound_dictionary_round_start_client_team_winning_massively =\
            self._load_sound_files("round-start-client-winning-massively")
        self._sound_dictionary_round_start_enemy_team_winning_massively =\
            self._load_sound_files("round-start-enemy-winning-massively")

        self._sound_dictionary_bomb_planted_client_team = self._load_sound_files("bomb-planted-client")

    def _load_sound_files(self, path):
        sound_files_array = []
        search_path = self._program.get_path_sounds() + path + os.path.sep

        try:
            for file in os.listdir(search_path):
                if file.endswith(".wav"):
                    sound_files_array.append(path + os.path.sep + file)
        except FileNotFoundError as e:
            print("Warning: " + search_path + " " + "is empty.")

        return sound_files_array

    def set_round_time(self, time_in_seconds):
        self._round_time_in_seconds = time_in_seconds

    def set_max_rounds(self, rounds):
        self._max_rounds = rounds
        
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
        if time.time() > self._started_saying_something_timestamp_in_seconds + self._last_file_duration_in_seconds:
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
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_enemy_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        elif (event_id == self.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_ENEMY_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_client_team)
            self._handle_event_audio_files(file_client, file_enemy)

        elif (event_id == self.SOUND_ID_KILL_KNIFE_CLIENT_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_KNIFE_CLIENT_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_enemy_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        elif (event_id == self.SOUND_ID_KILL_KNIFE_ENEMY_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_KNIFE_ENEMY_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_client_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        # *************** Time **************
                
        elif event_id == self.SOUND_ID_TIME_0_20 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_20)
            self._handle_event_audio_files(file_client, file_client)
            return True
                
        elif event_id == self.SOUND_ID_TIME_0_10 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_10)
            self._handle_event_audio_files(file_client, file_client)
            return True
                
        elif event_id == self.SOUND_ID_TIME_0_30 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_30)
            self._handle_event_audio_files(file_client, file_client)
            return True
                
        elif event_id == self.SOUND_ID_TIME_0_30 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_30)
            self._handle_event_audio_files(file_client, file_client)
            return True
                
        # *************** Teamkiller **************
                
        elif event_id == self.SOUND_ID_TEAMKILLER_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_TEAMKILLER_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_enemy_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        elif event_id == self.SOUND_ID_TEAMKILLER_ENEMY_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_TEAMKILLER_ENEMY_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_client_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        # *************** Scores ***************
        
        elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        elif event_id == self.SOUND_ID_SCORE_ENEMY_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_ENEMY_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
        
        elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_2_3 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_2_3)
            self._handle_event_audio_files(file_client)
            return True
                
        elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_3_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_3_1)
            self._handle_event_audio_files(file_client)
            return True
                
        elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_4_0 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_4_0)
            self._handle_event_audio_files(file_client)
            return True
                
        elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_5_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_5_1)
            self._handle_event_audio_files(file_client)
            return True
                
        elif event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_6_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_6_1)
            self._handle_event_audio_files(file_client)
            return True
        
        # *************** Round Start ***************
        
        elif event_id == self.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING \
        and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_client_team_winning)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_enemy_team_winning)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        elif event_id == self.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING \
        and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_enemy_team_winning)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_client_team_winning)
            self._handle_event_audio_files(file_client, file_enemy)
            return True
                
        # *************** Bomb planted ***************
        
        elif event_id == self.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_BOMB_PLANTED_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_bomb_planted_client_team)
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
            self._last_file_duration_in_seconds = self._get_file_duration(file_path)
            self._started_saying_something_timestamp_in_seconds = time.time()
            winsound.PlaySound(file_path, winsound.SND_ASYNC)
            
    def _get_file_duration(self, file_path):
        with contextlib.closing(wave.open(file_path,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
        
    def get_client_team_points(self):
        if self._program.get_client_team() == 1:
            return self._team1_points
        
        return self._team2_points
    
    def get_enemy_team_points(self):
        if self._program.get_client_team() == 1:
            return self._team2_points
        
        return self._team1_points
    
    def _get_client_team_side(self):
        if self._program.get_client_team() == 1:
            return self._team1_side
        
        return self._team2_side
        
    # @return Time left in seconds
    def _get_round_time_left(self):
        if self._round_start_timestamp_in_seconds is not 0:
            return int(self._round_time_in_seconds -  self._get_match_time_passed())
        return -1
        
    # @return Match time passed in seconds
    def _get_match_time_passed(self):
        if self._round_start_timestamp_in_seconds is not 0:
            return int(time.time() - self._round_start_timestamp_in_seconds)
        return -1
    
    def set_round_start_time(self, time_in_seconds):
        self._round_start_timestamp_in_seconds = time_in_seconds
    
    def reset_points(self):
        print("Reseting team points")
        self._team1_points = 0
        self._team2_points = 0
        
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
            return self._team1_points
        elif team_id == 2:
            return self._team2_points

    # @param side string ct or t
    def set_team_points(self, side, points):
        # If old points are greater than the new value, then we know that a new match as started
        if self._team1_side == side and points < self._team1_points:
            self.reset_points()
        elif self._team2_side == side and points < self._team2_points:
            self.reset_points()
        
        # Remember old values before changing them
        client_team_points_old = self.get_client_team_points()
        enemy_team_points_old = self.get_enemy_team_points()
        
        # Give the points to the team that plays on that side
        if self._team1_side == side:
            print("Team 1 scored {}".format(points))
            self._team1_points = points
        elif self._team2_side == side:
            print("Team 2 scored {}".format(points))
            self._team2_points = points
            
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
            return self._team1_side
        if team_number == 2:
            return self._team2_side

    # @param side string ct or t
    def set_team_side(self, team_number, side):
        if team_number == 1:
            self._team1_side = side
        if team_number == 2:
            self._team2_side = side
            
        if self._program.get_client_team() == team_number:
            print("The client plays now on {} side".format(side))