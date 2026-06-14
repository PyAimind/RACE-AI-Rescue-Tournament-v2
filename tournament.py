from race_manager import RaceManager

class Tournament:
    def __init__(self, map_filenames, team_names):
        self.map_filenames = map_filenames
        self.team_names = team_names
        self.tokens = {name: 0 for name in team_names}

    def run(self):
        for map_file in self.map_filenames:
            race = RaceManager(map_file, self.team_names)
            winner = race.run_race()
            self.tokens[winner] += 1
        return self.get_champion()

    def get_champion(self):
        return max(self.tokens, key=self.tokens.get)

    def get_leaderboard(self):
        return self.tokens