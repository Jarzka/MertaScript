import time
import os
import re
import commentator

class LogReader():
    def __init__(self, program):
        self._program = program
        self._commentator = None
        self._read_file_interval_in_seconds = 1 # How often the program scans the log file
        self._read_file_timestamp_in_seconds = 0
        self._check_newest_log_file_interval_in_seconds = 2 * 60
        self._check_newest_log_file_timestamp_in_seconds = 0
        self._log_file_max_age_in_seconds = 5 * 60
        self._current_log_file = ""
        self._read_lines = 0 # How many lines have been read from the log file

        self._PATH_SOUNDS = "sound" + os.path.sep
        self._PATH_SOUNDS += self._program.get_value_from_config_file("host_sounds_folder")
        self._PATH_SOUNDS += os.path.sep
        self._PATH_LOGS = self._program.get_value_from_config_file("host_logs_path")
        if self._PATH_LOGS[len(self._PATH_LOGS) - 1] is not os.path.sep: # Make sure that the path log ends with a backslash
            self._PATH_LOGS += os.path.sep

    def set_commentator(self, commentator):
        self._commentator = commentator

    def initialize(self):
        self._current_log_file =  self._find_most_recently_edited_log_file()

    def update_state(self):
        if (time.time() < self._read_file_timestamp_in_seconds + self._read_file_interval_in_seconds):
            return False

        self._read_file_timestamp_in_seconds = time.time()

        self._current_log_file = self._check_newest_log_file(self._current_log_file)
        self._read_file(self._current_log_file)

        return True

    def get_path_sounds(self):
        return self._PATH_SOUNDS

    # Finds the file that has been edited most recently (and it's not too old)
    def _find_most_recently_edited_log_file(self):
        print("Finding the most suitable log file...")

        most_recently_edited_file_name = None
        most_recently_edited_file_time = 0

        while most_recently_edited_file_name is None:
            try:
                for fileName in os.listdir(self._PATH_LOGS):
                    modification_time = os.path.getmtime(self._PATH_LOGS + fileName)
                    if time.time() < modification_time + (self._log_file_max_age_in_seconds): # The file has been modified recently
                        if modification_time > most_recently_edited_file_time: # The modification timestamp is newer than the previous one
                            most_recently_edited_file_time = modification_time
                            most_recently_edited_file_name = fileName
                    else:
                        print("Found file {}, but it is too old. Searching more...".format(fileName))
            except FileNotFoundError as e:
                print("Warning: log folder is empty.")

            # File not found, pause and try again
            if most_recently_edited_file_name is None:
                time.sleep(2)

        print("Found suitable file {}".format(most_recently_edited_file_name))
        return most_recently_edited_file_name

    # Returns the most recently edited log file if over x seconds have passed since the last
    # call of this method. If x seconds have not passed, returns file_name
    def _check_newest_log_file(self, file_name):
        if (time.time() < self._check_newest_log_file_timestamp_in_seconds
            + self._check_newest_log_file_interval_in_seconds):
            return file_name

        print("Checking the newest log file...")
        self._check_newest_log_file_timestamp_in_seconds = time.time()
        file_name_newest =  self._find_most_recently_edited_log_file()

        if not file_name_newest == file_name:
            print("Switching the newest log file from" + " " + file_name + " " + "to" + " " + file_name_newest)
            self._read_lines = 0

        return file_name_newest

    # Opens the file and processes it. Remembers how many lines have been processed and only affects the new lines
    def _read_file(self, file_name):
        print("{} Reading log file...".format(time.strftime("%H:%M:%S")))
        unread_lines = []

        try:
            file = open(self._PATH_LOGS + file_name, "r")
            unread_lines = []
            i = 1
            for line in file:
                if i > self._read_lines: # This line has not been read yet
                    unread_lines.append(line)
                    self._read_lines += 1
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
        for name in self._commentator.get_team_1_player_names():
            regEx += name
            if currentName is not len(self._commentator.get_team_1_player_names()): # Not the last name
                regEx += "|"
            currentName += 1
        regEx += ")"
        return regEx

    # Scans a single line and searches for interesting events
    def _scan_line(self, line):
        # Start from the common ones to save performance
        if self._scan_line_team1_teamkiller(line):
            return True
        if self._scan_line_team2_teamkiller(line):
            return True
        if self._scan_line_team1_kills_enemy_headshot(line):
            return True
        if self._scan_line_team2_kills_enemy_headshot(line):
            return True
        if self._scan_line_team1_kills_enemy_knife(line):
            return True
        if self._scan_line_team2_kills_enemy_knife(line):
            return True
        if self._scan_line_team1_kills_enemy_hegrenade(line):
            return True
        if self._scan_line_team2_kills_enemy_hegrenade(line):
            return True
        if self._scan_line_team1_kills_enemy_inferno(line):
            return True
        if self._scan_line_team2_kills_enemy_inferno(line):
            return True
        if self._scan_line_suicide(line):
            return True
        if self._scan_line_round_start(line):
            return True
        if self._scan_line_round_end(line):
            return True
        if self._scan_line_score_ct(line):
            return True
        if self._scan_line_score_t(line):
            return True
        if self._scan_line_team1_player_joins_team(line):
            return True
        if self._scan_line_max_rounds(line):
            return True
        if self._scan_line_round_time(line):
            return True
        if self._scan_line_bomb_plant(line):
            return True
        if self._scan_line_loading_map(line):
            return True
        if self._scan_line_game_end(line):
            return True
        return False

    def _scan_line_team1_teamkiller(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".* killed .*"
        reg_ex += self._construct_regex_team1()
        match = re.search(reg_ex, line)
        if match:
            print("Catch: {}".format(line))
            print("Teamkiller in team 1!")
            if self._commentator.get_client_team() == 1:
                self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
            elif self._commentator.get_client_team() == 2:
                self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
                return True
        return False

    def _scan_line_team2_teamkiller(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed someone who does not play in team 1.
        # However, it is very likely that the player was team 2 player and he killed team 2 player.

        reg_ex = ".* killed .*"
        match = re.search(reg_ex, line)
        if match:
            # This is a good match if there is NO team 1 player name BEFORE or AFTER the word killed
            if not self._is_team_1_player_the_killer(match.group(0)) \
            and not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                print("Teamkiller in team 2!")
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_ENEMY_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_TEAMKILLER_CLIENT_TEAM)
                return True
        return False

    def _scan_line_team1_kills_enemy_headshot(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".* killed .*"
        reg_ex += "headshot"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
                return True
        return False

    def _scan_line_team2_kills_enemy_headshot(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player.
        # However, it is very likely that the killer was team 2 player.

        reg_ex = ".* killed .*"
        reg_ex += self._construct_regex_team1()
        reg_ex += ".+headshot"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_killer(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1: #
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_ENEMY_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEADSHOT_CLIENT_TEAM)
                return True
        return False

    def _scan_line_team1_kills_enemy_knife(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".* killed .*"
        reg_ex += "with.+"
        reg_ex += "knife"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
                return True
        return False

    def _scan_line_team2_kills_enemy_knife(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player.
        # However, it is very likely that the killer was team 2 player.

        reg_ex = ".* killed .*"
        reg_ex += self._construct_regex_team1()
        reg_ex += ".+with.+"
        reg_ex += "knife"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_killer(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_ENEMY_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_KNIFE_CLIENT_TEAM)
                return True
        return False

    def _scan_line_team1_kills_enemy_hegrenade(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".* killed .*"
        reg_ex += "with.+"
        reg_ex += "hegrenade"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEGRENADE_CLIENT_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEGRENADE_ENEMY_TEAM)
                return True
        return False

    def _scan_line_team2_kills_enemy_hegrenade(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player.
        # However, it is very likely that the killer was team 2 player.

        reg_ex = ".* killed .*"
        reg_ex += self._construct_regex_team1()
        reg_ex += ".+with.+"
        reg_ex += "hegrenade"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_killer(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEGRENADE_ENEMY_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_HEGRENADE_CLIENT_TEAM)
                return True
        return False

    def _scan_line_team1_kills_enemy_inferno(self, line):
        reg_ex = self._construct_regex_team1()
        reg_ex += ".* killed .*"
        reg_ex += "with.+"
        reg_ex += "inferno"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_victim(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_INFERNO_CLIENT_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_INFERNO_ENEMY_TEAM)
                return True
        return False

    def _scan_line_team2_kills_enemy_inferno(self, line):
        # Actually the RegEx thinks that someone, who does not play in team 1, killed team 1 player.
        # However, it is very likely that the killer was team 2 player.

        reg_ex = ".* killed .*"
        reg_ex += self._construct_regex_team1()
        reg_ex += ".+with.+"
        reg_ex += "inferno"
        match = re.search(reg_ex, line)

        if match:
            if not self._is_team_1_player_the_killer(match.group(0)):
                print("Catch: {}".format(line))
                if self._commentator.get_client_team() == 1:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_INFERNO_ENEMY_TEAM)
                elif self._commentator.get_client_team() == 2:
                    self._commentator.handle_event(commentator.Commentator.SOUND_ID_KILL_INFERNO_CLIENT_TEAM)
                return True
        return False

    def _scan_line_suicide(self, line):
        reg_ex = ".+committed suicide.+"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            self._commentator.handle_event(commentator.Commentator.SOUND_ID_SUICIDE)
            return True
        return False

    def _scan_line_round_start(self, line):
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

    def _scan_line_round_end(self, line):
        reg_ex = ".*World triggered.*"
        reg_ex += "Round_End"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            self._commentator.set_round_start_time(0)
            return True
        return False

    def _scan_line_score_t(self, line):
        # L 08/01/2013 - 23:33:38: Team "TERRORIST" scored "4" with "5" players

        reg_ex = "Team.+"
        reg_ex += "\"TERRORIST\".+"
        reg_ex += "scored.+?"
        reg_ex += "\d"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            # We need to get the score points. Do this by selecting the digits from the match
            match2 = re.search("\d+", match.group(0))
            self._commentator.set_team_points("t", int(match2.group(0)))
            return True
        return False

    def _scan_line_score_ct(self, line):
        # L 08/01/2013 - 23:33:38: Team "CT" scored "1" with "5" players

        reg_ex = "Team.+"
        reg_ex += "\"CT\".+"
        reg_ex += "scored.+?"
        reg_ex += "\d"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            # We need to get the score points. Do this by selecting the digits from the match
            match2 = re.search("\d+", match.group(0))
            if match2:
                self._commentator.set_team_points("ct", int(match2.group(0)))
                return True
        return False

    def _scan_line_team1_player_joins_team(self, line):
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

    def _scan_line_max_rounds(self, line):
        reg_ex = "mp_maxrounds.+?\d"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            # We need to get the value. Do this by selecting the digits from the match
            match2 = re.search("\d+", match.group(0))
            if match2:
                max_rounds = int(match2.group(0))
                self._commentator.set_max_rounds(max_rounds)
                print("Max rounds changed to {}".format(max_rounds))
            return True
        return False

    def _scan_line_round_time(self, line):
        reg_ex = "mp_roundtime.+?\d"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            # We need to get the value. Do this by selecting the digits from the match
            match2 = re.search("\d+", match.group(0))
            if match2:
                round_time = int(match2.group(0))
                round_time *= 60
                self._commentator.set_round_time(round_time)
                print("Round time changed to {} seconds".format(round_time))
            return True
        return False

    def _scan_line_bomb_plant(self, line):
        reg_ex = "triggered.+"
        reg_ex += "Planted_The_Bomb"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            if self._commentator.get_team_side(self._commentator.get_client_team()) == "t":
                self._commentator.handle_event(commentator.Commentator.SOUND_ID_BOMB_PLANTED_CLIENT_TEAM)
            return True
        return False

    def _scan_line_loading_map(self, line):
        reg_ex = "Loading map"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            self._commentator.reset_points()
            self._commentator.reset_round_time();
            return True
        return False

    def _scan_line_game_end(self, line):
        reg_ex = "Log file closed"
        match = re.search(reg_ex, line)

        if match:
            print("Catch: {}".format(line))
            return True
        return False