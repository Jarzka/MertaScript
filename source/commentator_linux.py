# This is the commentator class.
# - Check that all audio files exist
# - Play audio files
# - Knows team points and round time

import wave
import contextlib
import time
import random
import os
import subprocess

class Commentator():
    # These constants are used to tell the commentator which type of sound file it's supposed to say
    SOUND_ID_KILL_CLIENT_TEAM = 1 # Not used atm
    SOUND_ID_KILL_ENEMY_TEAM = 3
    SOUND_ID_KILL_HEADSHOT_JUHIS_CLIENT_TEAM = 3742885738952 # A player whose name is Juhis in client team killed an enemy with headshot
    SOUND_ID_KILL_HEADSHOT_MACHINE_GUN_CLIENT_TEAM = 3342534738952 # Client team killed an enemy with machine got and got headshot
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
    SOUND_ID_SCORE_CLIENT_TEAM_1_0 = 45448 # Client team got a point and the scores are 1 for client and 0 for enemy
    SOUND_ID_SCORE_CLIENT_TEAM_1_1 = 83343 #
    SOUND_ID_SCORE_CLIENT_TEAM_2_0 = 8333343 #
    SOUND_ID_SCORE_CLIENT_TEAM_2_1 = 5343 #
    SOUND_ID_SCORE_CLIENT_TEAM_2_2 = 53643 #
    SOUND_ID_SCORE_CLIENT_TEAM_3_0 = 234 #
    SOUND_ID_SCORE_CLIENT_TEAM_3_2 = 23774 #
    SOUND_ID_SCORE_CLIENT_TEAM_3_1 = 8 #
    SOUND_ID_SCORE_CLIENT_TEAM_4_0 = 9 # ...
    SOUND_ID_SCORE_CLIENT_TEAM_5_1 = 10 # ...
    SOUND_ID_SCORE_CLIENT_TEAM_6_1 = 11 # ...
    SOUND_ID_SCORE_CLIENT_TEAM_2_3 = 23 # ...
    SOUND_ID_SCORE_ENEMY_TEAM_1_0 = 4544338 # Enemy team got a point and the scores are 0 for client and 1 for enemy
    SOUND_ID_SCORE_ENEMY_TEAM_2_0 = 455888 # ...
    SOUND_ID_SCORE_ENEMY_TEAM_3_1 = 43338 # ...
    SOUND_ID_SCORE_EVEN = 242422523 # ...
    SOUND_ID_DEFUSE_CLIENT_TEAM = 567473424654 # ...
    SOUND_ID_HOSTAGE_TAKEN_ENEMY_TEAM = 56747333424654 # ..
    SOUND_ID_WIN_CLIENT = 24242256623 # ...
    SOUND_ID_WIN_ENEMY = 24242233523 # ...
    SOUND_ID_SCORE_DEFUSE_BOMB_ENEMY_TEAM = 19 # Enemy team got a point by defusing the bomb
    SOUND_ID_TIME_0_02 = 33244442 # 2 seconds left
    SOUND_ID_TIME_0_03 = 3322 # ...
    SOUND_ID_TIME_0_10 = 13 # ...
    SOUND_ID_TIME_0_15 = 2213 # ...
    SOUND_ID_TIME_0_28 = 26724343785 # ...
    SOUND_ID_TIME_0_20 = 15 # ...
    SOUND_ID_TIME_0_30 = 14 # ...
    SOUND_ID_TIME_0_40 = 15454 # ...
    SOUND_ID_TIME_1_00 = 153342 # ...
    SOUND_ID_ROUND_DRAW = 166767544646
    SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING = 16 # Round started and the client team has more points
    SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING_MASSIVELY = 16344
    SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING = 17 # Round started and the enemy team has more points
    SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING_MASSIVELY = 1754
    SOUND_ID_BOMB_PLANTED_CLIENT_TEAM = 18 # Client's team planted the bomb
    
    # These values present how likely it is that the commentator will say the asked event id
    PROBABILITY_KILL_CLIENT_TEAM = 10 # Not used atm
    PROBABILITY_KILL_ENEMY_TEAM = 10
    PROBABILITY_KILL_HEADSHOT_JUHIS_CLIENT_TEAM = 15
    PROBABILITY_KILL_HEADSHOT_MACHINE_GUN_CLIENT_TEAM = 100
    PROBABILITY_KILL_HEADSHOT_CLIENT_TEAM = 100 
    PROBABILITY_KILL_HEADSHOT_ENEMY_TEAM = 100
    PROBABILITY_KILL_KNIFE_CLIENT_TEAM = 100 
    PROBABILITY_KILL_KNIFE_ENEMY_TEAM = 100
    PROBABILITY_KILL_HEGRENADE_CLIENT_TEAM = 100
    PROBABILITY_KILL_HEGRENADE_ENEMY_TEAM = 100
    PROBABILITY_KILL_INFERNO_CLIENT_TEAM = 100
    PROBABILITY_KILL_INFERNO_ENEMY_TEAM = 100
    PROBABILITY_TEAMKILLER_CLIENT_TEAM = 100
    PROBABILITY_TEAMKILLER_ENEMY_TEAM = 100
    PROBABILITY_SCORE_ENEMY_TEAM = 100
    PROBABILITY_SCORE_CLIENT_TEAM = 100
    PROBABILITY_DEFUSE_CLIENT_TEAM = 30
    PROBABILITY_HOSTAGE_TAKEN_ENEMY_TEAM = 30
    PROBABILITY_WIN_CLIENT = 100
    PROBABILITY_WIN_ENEMY = 100
    PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC = 100
    PROBABILITY_SCORE_ENEMY_TEAM_SPECIFIC = 100
    PROBABILITY_SUICIDE = 100
    PROBABILITY_TIME = 30
    PROBABILITY_ROUND_DRAW = 100
    PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING = 40
    PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING_MASSIVELY = 70
    PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING = 40
    PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING_MASSIVELY = 70
    PROBABILITY_BOMB_PLANTED_CLIENT_TEAM = 5
    
    def __init__(self, program, log_reader):
        self._play_process = None
        self._program = program
        self._log_reader = log_reader

        self._started_saying_something_timestamp_in_seconds = 0
        self._last_audio_file_duration_in_seconds = 0
        self._round_start_timestamp_in_seconds = 0
        self._check_time_interval_in_seconds = 1
        self._check_time_timestamp_in_seconds = 0
        self._team1_side = "" # ct or t
        self._team2_side = ""
        self._team1_points = 0
        self._team2_points = 0
        self._round_time_in_seconds = int(self._program.get_value_from_config_file("host_round_time"))
        self._max_rounds = int(self._program.get_value_from_config_file("host_max_rounds"))
        self._c4_time = int(self._program.get_value_from_config_file("host_c4_time"))
        self._hostage_taken_time_bonus = int(self._program.get_value_from_config_file("host_hostage_taken_time_bonus"))
        self._hostage_taken_time_bonus_given_in_this_round = False

        self._CLIENT_TEAM = int(self._program.get_value_from_config_file("client_team"))
        self._TEAM_1_PLAYER_NAMES = self._program.get_team_1_player_names_from_config_file()
        if self._CLIENT_TEAM is not 1 and self._CLIENT_TEAM is not 2:
            raise RuntimeError("config.txt client_team should be 1 or 2.")

        # Initialise dictionaries

        self._sound_dictionary_kill_headshot_juhis_client_team = self._load_sound_files("kill-headshot-juhis-client")
        self._sound_dictionary_kill_headshot_machine_gun_client_team = self._load_sound_files("kill-headshot-machine-gun-client")
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

        self._sound_dictionary_defuse_client_team = self._load_sound_files("defuse-client")

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
        self._sound_dictionary_score_enemy_team_1_0 = self._load_sound_files("score-enemy-1-0")
        self._sound_dictionary_score_enemy_team_2_0 = self._load_sound_files("score-enemy-2-0")
        self._sound_dictionary_score_enemy_team_3_1 = self._load_sound_files("score-enemy-3-1")
        self._sound_dictionary_score_even_client_team = self._load_sound_files("score-even-client")
        self._sound_dictionary_score_enemy_team = self._load_sound_files("score-enemy")
        self._sound_dictionary_score_win_client_team = self._load_sound_files("score-win-client")
        self._sound_dictionary_score_win_enemy_team = self._load_sound_files("score-win-enemy")

        self._sound_dictionary_suicide = self._load_sound_files("suicide")

        self._sound_dictionary_time_0_02 = self._load_sound_files("time-0-02")
        self._sound_dictionary_time_0_03 = self._load_sound_files("time-0-03")
        self._sound_dictionary_time_0_10 = self._load_sound_files("time-0-10")
        self._sound_dictionary_time_0_15 = self._load_sound_files("time-0-15")
        self._sound_dictionary_time_0_20 = self._load_sound_files("time-0-20")
        self._sound_dictionary_time_0_28 = self._load_sound_files("time-0-28")
        self._sound_dictionary_time_0_30 = self._load_sound_files("time-0-30")
        self._sound_dictionary_time_0_40 = self._load_sound_files("time-0-40")
        self._sound_dictionary_time_1_00 = self._load_sound_files("time-1-00")

        self._sound_dictionary_round_draw = self._load_sound_files("round-draw")
        self._sound_dictionary_round_start_client_team_winning = self._load_sound_files("round-start-client-winning")
        self._sound_dictionary_round_start_enemy_team_winning = self._load_sound_files("round-start-enemy-winning")
        self._sound_dictionary_round_start_client_team_winning_massively =\
            self._load_sound_files("round-start-client-winning-massively")
        self._sound_dictionary_round_start_enemy_team_winning_massively =\
            self._load_sound_files("round-start-enemy-winning-massively")

        self._sound_dictionary_bomb_planted_client_team = self._load_sound_files("bomb-planted-client")

        self._sound_dictionary_hostage_taken_enemy_team = self._load_sound_files("hostage-taken-enemy")

    def get_team_1_player_names(self):
        return self._TEAM_1_PLAYER_NAMES

    def get_client_team(self):
        return self._CLIENT_TEAM

    def get_enemy_team(self):
        if self._CLIENT_TEAM == 1:
            return 2
        elif self._CLIENT_TEAM == 2:
            return 1

    def _load_sound_files(self, path):
        sound_files_array = []
        search_path = self._log_reader.get_path_sounds() + path + os.path.sep

        try:
            for file in os.listdir(search_path):
                if file.endswith(".wav"):
                    # TODO Temporary fix.
                    # For some reason Python 3 is unable to handle the following characters correctly. Correct them manually.
                    file = file.replace("\udce4", "ä");
                    file = file.replace("\udcf6", "ö");
                    sound_files_array.append(path + os.path.sep + file)
        except FileNotFoundError as e:
            print("Warning: " + search_path + " " + "is empty.")

        return sound_files_array
        

    def set_round_time(self, time_in_seconds):
        self._round_time_in_seconds = time_in_seconds
        self._round_start_timestamp_in_seconds = 0

    def set_max_rounds(self, rounds):
        self._max_rounds = rounds

    def set_c4_time(self, time):
        self._c4_time = time

    def set_time_left_to_c4_time(self):
        # The easiest way to set the new amount of remaining time is to "fake" the round start timestamp.
        # This may not be the most convenient way to solve this problem, but it works and does not
        # cause problems.
        self.set_round_start_time(time.time() - self._round_time_in_seconds + self._c4_time)

    def add_hostage_taken_time_bonus_if_necessery(self):
        # The easiest way to set the new amount of remaining time is to "fake" the round start timestamp.
        # This may not be the most convenient way to solve this problem, but it works and does not
        # cause problems.
        if self._hostage_taken_time_bonus_given_in_this_round is False:
            self.set_round_start_time(time.time() - self._get_round_time_passed() + self._hostage_taken_time_bonus)
            self._hostage_taken_time_bonus_given_in_this_round = True

    # The method randomly chooses a sound file from the given dictionary and returns it.
    # @param dictionary. key = SOUND_ID, value = file.wav
    def _select_dictionary_sound_randomly(self, dictionary):
        if len(dictionary) == 0:
                file = dictionary[0]
                return file

        random.shuffle(dictionary)
        pseudo_random_number = random.randrange(0, len(dictionary))
        
        # Make sure the number we got is not bigger than len(dictionary) or less than 0
        while pseudo_random_number > len(dictionary) - 1 or pseudo_random_number < 0:
                pseudo_random_number = random.randrange(0, len(dictionary))
        
        file = dictionary[pseudo_random_number]
        print("Choosing sound from the dictionary: {}".format(file))
        return file
    
    def _is_currently_saying_something(self):
        if time.time() > self._started_saying_something_timestamp_in_seconds + self._last_audio_file_duration_in_seconds:
            return False
        
        return True
    
    # @param percent int a number between 0 - 100. The higher it is the more likely it is that his function returns True
    def _get_bool_from_percent(self, percent):
        value = random.randrange(0, 101)
        # print(value2)
        if percent >= value:
            return True
        return False
    
    # This method will ask Network Manager to send a PLAY_SOUND command to all clients
    # @param file_Same_team string Audio file name to be sent for the clients who play in the same team as host
    # @param file_different_team string Audio file name to be sent for the clients who play in different team than host
    def _send_play_sound_command_to_clients(self, file_client_team = None, file_enemy_team = None):
        if file_client_team is not None:
            self._program.get_network_manager().send_message_to_clients("<" + "PLAY_SOUND|" + file_client_team  +">",
                                                                        self.get_client_team())
        if file_enemy_team is not None:
            self._program.get_network_manager().send_message_to_clients("<" + "PLAY_SOUND|" + file_enemy_team + ">",
                                                                             self.get_enemy_team())
    
    # Play an audio file related to the given eventId. Will also send the play audio command to clients
    def handle_event(self, event_id):
        # Every function call below checks the probability of playing an audio file from a specific dictionary
        # and decides if it is played.

        # ************** Kills **************

        if self._handle_event_kill_headshot_machine_gun_client(event_id): return True
        if self._handle_event_kill_headshot_juhis_client(event_id): return True
        if self._handle_event_kill_headshot_client(event_id): return True
        if self._handle_event_kill_headshot_enemy(event_id): return True
        if self._handle_event_kill_knife_client(event_id): return True
        if self._handle_event_kill_knife_enemy(event_id): return True
        if self._handle_event_kill_hegrenade_client(event_id): return True
        if self._handle_event_kill_hegrenade_enemy(event_id): return True
        if self._handle_event_kill_inferno_client(event_id): return True
        if self._handle_event_kill_inferno_enemy(event_id): return True
                
        # *************** Time **************

        if self._handle_event_time_0_02(event_id): return True
        if self._handle_event_time_0_03(event_id): return True
        if self._handle_event_time_0_10(event_id): return True
        if self._handle_event_time_0_15(event_id): return True
        if self._handle_event_time_0_20(event_id): return True
        if self._handle_event_time_0_28(event_id): return True
        if self._handle_event_time_0_30(event_id): return True
        if self._handle_event_time_0_40(event_id): return True
        if self._handle_event_time_1_00(event_id): return True

        # *************** Teamkiller **************
                
        if self._handle_event_timeakiller_client(event_id): return True
        if self._handle_event_teamkiller_enemy(event_id): return True

        # *************** Suicide ***************

        if self._handle_event_suicide(event_id): return True

        # *************** Scores ***************
        
        if self._handle_event_score_client(event_id): return True
        if self._handle_event_score_enemy(event_id): return True
        if self._handle_event_score_even(event_id): return True
        if self._handle_event_score_client_win(event_id): return True
        if self._handle_event_score_enemy_win(event_id): return True
        if self._handle_event_score_client_1_0(event_id): return True
        if self._handle_event_score_client_1_1(event_id): return True
        if self._handle_event_score_client_2_0(event_id): return True
        if self._handle_event_score_client_2_1(event_id): return True
        if self._handle_event_score_client_2_2(event_id): return True
        if self._handle_event_score_client_2_3(event_id): return True
        if self._handle_event_score_client_3_0(event_id): return True
        if self._handle_event_score_client_3_1(event_id): return True
        if self._handle_event_score_client_3_2(event_id): return True
        if self._handle_event_score_client_4_0(event_id): return True
        if self._handle_event_score_client_5_1(event_id): return True
        if self._handle_event_score_client_6_1(event_id): return True
        if self._handle_event_score_enemy_1_0(event_id): return True
        if self._handle_event_score_enemy_2_0(event_id): return True
        if self._handle_event_score_enemy_3_1(event_id): return True

        # *************** Round Draw ***************

        if self._handle_event_round_draw(event_id): return True

        # *************** Round Start ***************

        if self._handle_event_round_start(event_id): return True
                
        # *************** Bomb  ***************

        if self._handle_event_defuse_client(event_id): return True
        if self._handle_event_bomb_planted_client(event_id): return True

        # *************** Hostage  ***************

        if self._handle_event_hostage_taken_enemy(event_id): return True

        return False

    def _handle_event_kill_headshot_machine_gun_client(self, event_id):
        if (event_id == self.SOUND_ID_KILL_HEADSHOT_MACHINE_GUN_CLIENT_TEAM
            and self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_MACHINE_GUN_CLIENT_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_machine_gun_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_headshot_juhis_client(self, event_id):
        if event_id == self.SOUND_ID_KILL_HEADSHOT_JUHIS_CLIENT_TEAM:
            if self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_JUHIS_CLIENT_TEAM):
                file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_juhis_client_team)
                file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_enemy_team)
                self._handle_event_with_audio_files(file_client, file_enemy)
                return True
            else:
                return self._handle_event_kill_headshot_client(self.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)

        return False

    def _handle_event_kill_headshot_client(self, event_id):
        if (event_id == self.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_CLIENT_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_headshot_enemy(self, event_id):
        if (event_id == self.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_HEADSHOT_ENEMY_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_headshot_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_knife_client(self, event_id):
        if (event_id == self.SOUND_ID_KILL_KNIFE_CLIENT_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_KNIFE_CLIENT_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_knife_enemy(self, event_id):
        if (event_id == self.SOUND_ID_KILL_KNIFE_ENEMY_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_KNIFE_ENEMY_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_knife_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_hegrenade_client(self, event_id):
        if (event_id == self.SOUND_ID_KILL_HEGRENADE_CLIENT_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_HEGRENADE_CLIENT_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_hegrenade_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_hegrenade_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_hegrenade_enemy(self, event_id):
        if (event_id == self.SOUND_ID_KILL_HEGRENADE_ENEMY_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_HEGRENADE_ENEMY_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_hegrenade_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_hegrenade_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_inferno_client(self, event_id):
        if (event_id == self.SOUND_ID_KILL_INFERNO_CLIENT_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_INFERNO_CLIENT_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_inferno_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_inferno_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_kill_inferno_enemy(self, event_id):
        if (event_id == self.SOUND_ID_KILL_INFERNO_ENEMY_TEAM
        and self._get_bool_from_percent(self.PROBABILITY_KILL_INFERNO_ENEMY_TEAM)):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_inferno_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_kill_inferno_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_time_0_02(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_02 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_02)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_03(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_03 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_03)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_10(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_10 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_10)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_15(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_15 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_15)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_20(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_20 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_20)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_28(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_28 \
                and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_28)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_30(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_30 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_30)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_0_40(self, event_id):
        if event_id == self.SOUND_ID_TIME_0_40 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_0_40)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_time_1_00(self, event_id):
        if event_id == self.SOUND_ID_TIME_1_00 \
        and self._get_bool_from_percent(self.PROBABILITY_TIME):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_time_1_00)
            self._handle_event_with_audio_files(file_client, file_client)
            return True

        return False

    def _handle_event_timeakiller_client(self, event_id):
        if event_id == self.SOUND_ID_TEAMKILLER_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_TEAMKILLER_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_teamkiller_enemy(self, event_id):
        if event_id == self.SOUND_ID_TEAMKILLER_ENEMY_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_TEAMKILLER_ENEMY_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_teamkiller_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_suicide(self, event_id):
        if event_id == self.SOUND_ID_SUICIDE \
        and self._get_bool_from_percent(self.PROBABILITY_SUICIDE):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_suicide)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_suicide)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_enemy(self, event_id):
        if event_id == self.SOUND_ID_SCORE_ENEMY_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_ENEMY_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_even(self, event_id):
        if event_id == self.SOUND_ID_SCORE_EVEN \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_even_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_win_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_win(self, event_id):
        if event_id == self.SOUND_ID_WIN_CLIENT \
        and self._get_bool_from_percent(self.PROBABILITY_WIN_CLIENT):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_win_client_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_win_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_enemy_win(self, event_id):
        if event_id == self.SOUND_ID_WIN_ENEMY \
        and self._get_bool_from_percent(self.PROBABILITY_WIN_ENEMY):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_win_enemy_team)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_win_client_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_1_0(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_1_0 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_1_0)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team_1_0)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_1_1(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_1_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_1_1)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_2_0(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_2_0 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_2_0)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_2_1(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_2_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_2_1)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_2_2(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_2_2 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_2_2)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_2_3(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_2_3 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_2_3)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_3_0(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_3_0 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_3_0)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

    def _handle_event_score_client_3_1(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_3_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_3_1)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_3_2(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_3_2 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_3_2)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

    def _handle_event_score_client_4_0(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_4_0 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_4_0)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_5_1(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_5_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_5_1)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_client_6_1(self, event_id):
        if event_id == self.SOUND_ID_SCORE_CLIENT_TEAM_6_1 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_CLIENT_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_6_1)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_enemy_1_0(self, event_id):
        if event_id == self.SOUND_ID_SCORE_ENEMY_TEAM_1_0 \
        and self._get_bool_from_percent(self.PROBABILITY_SCORE_ENEMY_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team_1_0)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_1_0)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_enemy_2_0(self, event_id):
        if event_id == self.SOUND_ID_SCORE_ENEMY_TEAM_2_0 \
                and self._get_bool_from_percent(self.PROBABILITY_SCORE_ENEMY_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team_2_0)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_2_0)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_score_enemy_3_1(self, event_id):
        if event_id == self.SOUND_ID_SCORE_ENEMY_TEAM_3_1 \
                and self._get_bool_from_percent(self.PROBABILITY_SCORE_ENEMY_TEAM_SPECIFIC):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_score_enemy_team_3_1)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_score_client_team_3_1)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_round_draw(self, event_id):
        if event_id == self.SOUND_ID_ROUND_DRAW \
                and self._get_bool_from_percent(self.PROBABILITY_ROUND_DRAW):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_round_draw)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_round_draw)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_round_start(self, event_id):
        # Sometimes the round start event occurs in the game log after the match has ended.
        # This may be a bug in the logging system so do not handle the round start event
        # when the match has ended
        if self._team1_points < self._max_rounds / 2 and self._team2_points < self._max_rounds / 2:
            if self._handle_event_round_start_client_winning(event_id): return True
            if self._handle_event_round_start_enemy_team_winning(event_id): return True
            if self._handle_event_round_start_client_winning_massively(event_id): return True
            if self._handle_event_round_start_enemy_team_winning_massively(event_id): return True

        return False

    def _handle_event_round_start_client_winning(self, event_id):
        if event_id == self.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING \
        and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_client_team_winning)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_enemy_team_winning)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_round_start_enemy_team_winning(self, event_id):
        if event_id == self.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING \
        and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_enemy_team_winning)
            file_enemy = self._select_dictionary_sound_randomly(self._sound_dictionary_round_start_client_team_winning)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_round_start_client_winning_massively(self, event_id):
        if event_id == self.SOUND_ID_ROUND_START_CLIENT_TEAM_WINNING_MASSIVELY \
        and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_CLIENT_TEAM_WINNING_MASSIVELY):
            file_client = self._select_dictionary_sound_randomly(
                self._sound_dictionary_round_start_client_team_winning_massively)
            file_enemy = self._select_dictionary_sound_randomly\
                (self._sound_dictionary_round_start_enemy_team_winning_massively)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_round_start_enemy_team_winning_massively(self, event_id):
        if event_id == self.SOUND_ID_ROUND_START_ENEMY_TEAM_WINNING_MASSIVELY \
        and self._get_bool_from_percent(self.PROBABILITY_ROUND_START_ENEMY_TEAM_WINNING_MASSIVELY):
            file_client = self._select_dictionary_sound_randomly\
                (self._sound_dictionary_round_start_enemy_team_winning_massively)
            file_enemy = self._select_dictionary_sound_randomly\
                (self._sound_dictionary_round_start_client_team_winning_massively)
            self._handle_event_with_audio_files(file_client, file_enemy)
            return True

        return False

    def _handle_event_defuse_client(self, event_id):
        if event_id == self.SOUND_ID_DEFUSE_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_DEFUSE_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_defuse_client_team)
            self._handle_event_with_audio_files(file_client)
            return True

        return False

    def _handle_event_bomb_planted_client(self, event_id):
        if event_id == self.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_BOMB_PLANTED_CLIENT_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_bomb_planted_client_team)
            self._handle_event_with_audio_files(file_client)
            return True

        return False

    def _handle_event_hostage_taken_enemy(self, event_id):
        if event_id == self.SOUND_ID_HOSTAGE_TAKEN_ENEMY_TEAM \
        and self._get_bool_from_percent(self.PROBABILITY_HOSTAGE_TAKEN_ENEMY_TEAM):
            file_client = self._select_dictionary_sound_randomly(self._sound_dictionary_hostage_taken_enemy_team)
            self._handle_event_with_audio_files(file_client)
            return True

        return False
    
    # @param audioFileClient string The file to be played locally and to be send to clients who play in the same team than host
    # @param audioFileEnemy string The file to be sent to client who play in different team than the host
    def _handle_event_with_audio_files(self, audio_file_client, audio_file_enemy=None):
            self.play_file(self._log_reader.get_path_sounds() + audio_file_client) # Play audio file locally

            if self._program.get_network_manager().is_host():
                if audio_file_enemy is not None:
                    self._send_play_sound_command_to_clients(self._log_reader.get_path_sounds() + audio_file_client,
                                                         self._log_reader.get_path_sounds() + audio_file_enemy)
                else:
                    self._send_play_sound_command_to_clients(self._log_reader.get_path_sounds() + audio_file_client, None)
        
    def play_file(self, path):
        #if not self._is_currently_saying_something(): # Stop playing the previous comment and play the asked file
            self._last_audio_file_duration_in_seconds = self._get_file_duration(path)
            self._started_saying_something_timestamp_in_seconds = time.time()
            try:
                self._play_process.terminate()
            except Exception as e:
                print("Warning: Unable to terminate audio process: {}".format(e))
                
            try:
                print("Playing sound: {}".format(path))
                self._play_process = subprocess.Popen(['aplay', path])
            except Exception as e:
                print("Warning: Unable to play audio file: {}".format(e))
            
    def _get_file_duration(self, file_path):
        with contextlib.closing(wave.open(file_path,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
        
    def get_client_team_points(self):
        if self.get_client_team() == 1:
            return self._team1_points
        
        return self._team2_points
    
    def get_enemy_team_points(self):
        if self.get_client_team() == 1:
            return self._team2_points
        
        return self._team1_points
    
    def _get_client_team_side(self):
        if self.get_client_team() == 1:
            return self._team1_side
        
        return self._team2_side
        
    # @return Time left in seconds
    def _get_round_time_left(self):
        if self._round_start_timestamp_in_seconds is not 0:
            return int(self._round_time_in_seconds - self._get_round_time_passed())
        return -1
        
    # @return Match time passed in seconds
    def _get_round_time_passed(self):
        if self._round_start_timestamp_in_seconds is not 0:
            return int(time.time() - self._round_start_timestamp_in_seconds)
        return -1
    
    def start_new_round(self):
        self._round_start_timestamp_in_seconds = int(time.time())
        self._hostage_taken_time_bonus_given_in_this_round = False
	
    def set_round_start_time(self, time):
        self._round_start_timestamp_in_seconds = time

    def reset_points(self):
        print("Reseting team points")
        self._team1_points = 0
        self._team2_points = 0

    def reset_round_time(self):
        print("Reseting round time")
        self._round_start_timestamp_in_seconds = 0
        
    def update_state(self):
        if (time.time() < self._check_time_timestamp_in_seconds + self._check_time_interval_in_seconds):
            return False

        self._check_time()

        return True
        
    # Checks how much time is left and if it is possible to comment it
    def _check_time(self):
        self._check_time_timestamp_in_seconds = time.time()
        round_time_left = self._get_round_time_left()
        
        if round_time_left > 0:
            print("Round time left: {}".format(round_time_left))

        if round_time_left == 2:
            self.handle_event(self.SOUND_ID_TIME_0_02)
        if round_time_left == 3:
            self.handle_event(self.SOUND_ID_TIME_0_03)
        elif round_time_left == 10:
            self.handle_event(self.SOUND_ID_TIME_0_10)
        elif round_time_left == 15:
            self.handle_event(self.SOUND_ID_TIME_0_15)
        elif round_time_left == 20:
            self.handle_event(self.SOUND_ID_TIME_0_20)
        elif round_time_left == 28:
            self.handle_event(self.SOUND_ID_TIME_0_28)
        elif round_time_left == 30:
            self.handle_event(self.SOUND_ID_TIME_0_30)
        elif round_time_left == 40:
            self.handle_event(self.SOUND_ID_TIME_0_40)
        elif round_time_left == 60:
            self.handle_event(self.SOUND_ID_TIME_1_00)
        
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
            
        self._handle_event_score(client_team_points_old, enemy_team_points_old)

    def _handle_event_score(self, client_team_points_old, enemy_team_points_old):
        # Did client team got a new point?
        if self.get_client_team_points() > client_team_points_old:
            print("Client team got more points")

            # Did client win the match
            if self.get_client_team_points() > self._max_rounds / 2:
                self.handle_event(self.SOUND_ID_WIN_CLIENT)

            # Are the points specific?
            elif self.get_client_team_points() == 1 and self.get_enemy_team_points() == 0:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_1_0)
            elif self.get_client_team_points() == 1 and self.get_enemy_team_points() == 1:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_1_1)
            elif self.get_client_team_points() == 2 and self.get_enemy_team_points() == 0:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_2_0)
            elif self.get_client_team_points() == 2 and self.get_enemy_team_points() == 1:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_2_1)
            elif self.get_client_team_points() == 2 and self.get_enemy_team_points() == 3:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_2_3)
            elif self.get_client_team_points() == 3 and self.get_enemy_team_points() == 0:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_3_0)
            elif self.get_client_team_points() == 3 and self.get_enemy_team_points() == 1:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_3_1)
            elif self.get_client_team_points() == 3 and self.get_enemy_team_points() == 2:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_3_2)
            elif self.get_client_team_points() == 4 and self.get_enemy_team_points() == 0:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_4_0)
            elif self.get_client_team_points() == 5 and self.get_enemy_team_points() == 1:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_5_1)
            elif self.get_client_team_points() == 6 and self.get_enemy_team_points() == 1:
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM_6_1)
            elif self.get_client_team_points() == self.get_enemy_team_points():
                self.handle_event(self.SOUND_ID_SCORE_EVEN)
            else: # No specific score found, play the default sound
                self.handle_event(self.SOUND_ID_SCORE_CLIENT_TEAM)

        # Did enemy team got a new point?
        if self.get_enemy_team_points() > enemy_team_points_old:
            print("Enemy team got more points")

            # Did enemy win the match
            if self.get_enemy_team_points() > self._max_rounds / 2:
                self.handle_event(self.SOUND_ID_WIN_ENEMY)

            # Are the points specific?
            elif self.get_client_team_points() == 0 and self.get_enemy_team_points() == 1:
                self.handle_event(self.SOUND_ID_SCORE_ENEMY_TEAM_1_0)
            elif self.get_client_team_points() == 0 and self.get_enemy_team_points() == 2:
                self.handle_event(self.SOUND_ID_SCORE_ENEMY_TEAM_2_0)
            elif self.get_client_team_points() == 1 and self.get_enemy_team_points() == 3:
                self.handle_event(self.SOUND_ID_SCORE_ENEMY_TEAM_3_1)
            else:
                self.handle_event(self.SOUND_ID_SCORE_ENEMY_TEAM)

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
            
        if self.get_client_team() == team_number:
            print("The client plays now on {} side".format(side))