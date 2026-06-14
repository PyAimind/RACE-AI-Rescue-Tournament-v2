import json
import random
import os
from copy import deepcopy
from map_loader import load_map, get_grid
from team import Team

class RaceManager:
    def __init__(self, map_filename, team_names):
        map_data = load_map(map_filename)
        self.map_name = map_data['name']
        self.width = map_data['width']
        self.height = map_data['height']
        self.shared_grid = deepcopy(get_grid(map_data))
        self.teams = []
        self.q_table_dir = "q_tables"
        os.makedirs(self.q_table_dir, exist_ok=True)
        for name in team_names:
            team = Team(name, (0, 0), self.shared_grid)
            filepath = os.path.join(self.q_table_dir, f"{name}.json")
            if os.path.exists(filepath):
                team.brain.load_q_table(filepath)
            else:
                team.pretrain(episodes=50)
                team.brain.save_q_table(filepath)
            self.teams.append(team)
        self.current_turn = 0
        self.total_turns = 0
        self.max_turns = 500
        self.tokens = {name: 0 for name in team_names}
        self.extra_steps = {name: 0 for name in team_names}
        self.strategy_factor = {name: random.uniform(0.9, 1.1) for name in team_names}
        random.shuffle(self.teams)

    def _sync_target_removal(self, pos):
        self.shared_grid[pos[0]][pos[1]] = 0
        for team in self.teams:
            if pos in team.brain.targets:
                team.brain.targets.remove(pos)

    def all_targets_rescued(self):
        for row in self.shared_grid:
            if 4 in row:
                return False
        return True

    def step_turn(self):
        team = self.teams[self.current_turn]
        if not team.has_won():
            result = team.step()
            self.total_turns += 1
            if result == "rescued":
                self._sync_target_removal(team.get_position())
            elif result != "rescued":
                self.extra_steps[team.name] += 1
        self.current_turn = (self.current_turn + 1) % len(self.teams)
        return self.all_targets_rescued()

    def run_race(self):
        while self.total_turns < self.max_turns and not self.all_targets_rescued():
            finished = self.step_turn()
            if finished:
                break
        scores = self.get_leaderboard()
        max_score = max(scores.values())
        top_teams = [name for name, sc in scores.items() if sc == max_score]
        winner = random.choice(top_teams)
        self.tokens[winner] += 1
        for team in self.teams:
            filepath = os.path.join(self.q_table_dir, f"{team.name}.json")
            team.brain.save_q_table(filepath)
        return winner

    def calculate_score(self, team):
        return ((team.rescued_count * 10) - team.steps_taken - (self.extra_steps[team.name] * 0.5)) * self.strategy_factor[team.name]

    def get_winner(self):
        scores = self.get_leaderboard()
        max_score = max(scores.values())
        top_teams = [name for name, sc in scores.items() if sc == max_score]
        return random.choice(top_teams)

    def get_leaderboard(self):
        return {team.name: self.calculate_score(team) for team in self.teams}