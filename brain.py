import random
import json
import os
from collections import deque
from map_loader import get_cell

class BrainAgent:
    def __init__(self, map_grid, targets, alpha=0.3, gamma=0.9, epsilon=0.2):
        self.map_grid = map_grid
        self.targets = targets[:]
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.current_path = []
        self.current_goal_idx = None
        self.last_state = None
        self.last_target_idx = None
        self.memory = set()

    def bfs_path(self, start, goal):
        sx, sy = start
        gx, gy = goal
        visited = {(sx, sy)}
        q = deque([(sx, sy, [])])
        dirs = [(-1,0,'UP'), (1,0,'DOWN'), (0,-1,'LEFT'), (0,1,'RIGHT')]
        while q:
            x, y, path = q.popleft()
            for dx, dy, d in dirs:
                nx, ny = x+dx, y+dy
                cell = get_cell(self.map_grid, nx, ny)
                if cell == -1 or (nx, ny) in self.memory or cell == 2:
                    continue
                if (nx, ny) not in visited:
                    if (nx, ny) == (gx, gy):
                        return path + [d]
                    visited.add((nx, ny))
                    q.append((nx, ny, path + [d]))
        return []

    def choose_best_target(self, worker_pos):
        wx, wy = worker_pos
        if not self.targets:
            return None
        state = (wx, wy)
        if state not in self.q_table:
            self.q_table[state] = {}
        if random.random() < self.epsilon:
            idx = random.randrange(len(self.targets))
        else:
            q_vals = self.q_table[state]
            max_val = max([q_vals.get(i, 0.0) for i in range(len(self.targets))])
            candidates = [i for i in range(len(self.targets)) if q_vals.get(i, 0.0) == max_val]
            idx = random.choice(candidates)
        self.last_state = state
        self.last_target_idx = idx
        return idx

    def learn_from_outcome(self, reward, worker_pos):
        if self.last_state is None or self.last_target_idx is None:
            return
        state = self.last_state
        action = self.last_target_idx
        next_state = worker_pos
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0
        if next_state not in self.q_table:
            self.q_table[next_state] = {}
        max_next = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        old_val = self.q_table[state][action]
        self.q_table[state][action] = old_val + self.alpha * (reward + self.gamma * max_next - old_val)

    def choose_action(self, state):
        wx, wy = state[0], state[1]
        if (self.current_goal_idx is not None and
            self.current_goal_idx < len(self.targets) and
            self.targets[self.current_goal_idx] in self.targets):
            if self.current_path:
                return self.current_path.pop(0)
        target_idx = self.choose_best_target((wx, wy))
        if target_idx is None:
            return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.current_goal_idx = target_idx
        target_pos = self.targets[target_idx]
        path = self.bfs_path((wx, wy), target_pos)
        if not path:
            path = [random.choice(["UP", "DOWN", "LEFT", "RIGHT"])]
        self.current_path = path[:]
        return self.current_path.pop(0) if self.current_path else "UP"

    def update_q_value(self, reward, next_state):
        wx, wy = next_state[0], next_state[1]
        self.learn_from_outcome(reward, (wx, wy))

    def learn_danger(self, pos):
        self.memory.add(pos)

    def is_dangerous(self, pos):
        return pos in self.memory

    def save_q_table(self, filepath):
        serial = {f"{k[0]},{k[1]}": v for k, v in self.q_table.items()}
        with open(filepath, 'w') as f:
            json.dump(serial, f, indent=2)

    def load_q_table(self, filepath):
        if not os.path.exists(filepath):
            return
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.q_table = {}
        for key_str, actions in data.items():
            x, y = map(int, key_str.split(','))
            self.q_table[(x, y)] = {int(k): v for k, v in actions.items()}