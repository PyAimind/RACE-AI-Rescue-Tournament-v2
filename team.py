from worker import WorkerAgent
from brain import BrainAgent

class Team:
    def __init__(self, name, start_pos, map_grid, alpha=0.3, gamma=0.9, epsilon=0.2):
        self.name = name
        self.map_grid = map_grid
        self.targets = []
        for x, row in enumerate(map_grid):
            for y, cell in enumerate(row):
                if cell == 4:
                    self.targets.append((x, y))
        self.initial_targets = len(self.targets)
        self.worker = WorkerAgent(start_pos[0], start_pos[1], map_grid)
        self.brain = BrainAgent(map_grid, self.targets[:], alpha, gamma, epsilon)
        self.steps_taken = 0
        self.rescued_count = 0
        self.total_reward = 0
        self.done = False
        self.current_path = []

    def _should_allow_fire(self):
        return False

    def step(self):
        if self.done or len(self.brain.targets) == 0:
            self.done = True
            return "done"
        if not self.current_path:
            wx, wy = self.worker.get_position()
            idx = self.brain.choose_best_target((wx, wy))
            if idx is None:
                self.done = True
                return "done"
            goal = self.brain.targets[idx]
            path = self.brain.bfs_path((wx, wy), goal)
            if not path:
                self.steps_taken += 1
                reward = -5
                self.total_reward += reward
                self.brain.learn_from_outcome(reward, (wx, wy))
                return "blocked"
            self.current_path = path[:]
        direction = self.current_path.pop(0)
        (new_pos, event) = self.worker.move(direction, self._should_allow_fire())
        self.steps_taken += 1
        if event == "rescued":
            reward = 50
            self.rescued_count += 1
            if new_pos in self.brain.targets:
                self.brain.targets.remove(new_pos)
            self.current_path = []
        elif event == "hit_rubble":
            reward = -10
            self.current_path = []
        elif event == "hit_fire":
            reward = -50
            self.current_path = []
        elif event == "blocked":
            reward = -5
            self.current_path = []
        else:
            reward = -1
        self.total_reward += reward
        self.brain.learn_from_outcome(reward, (new_pos[0], new_pos[1]))
        if len(self.brain.targets) == 0:
            self.done = True
        return event

    def get_position(self):
        return self.worker.get_position()

    def has_won(self):
        return self.done or len(self.brain.targets) == 0

    def get_rescued_count(self):
        return self.initial_targets - len(self.brain.targets)

    def get_steps_count(self):
        return self.steps_taken

    def get_status(self):
        return {
            "name": self.name,
            "position": self.get_position(),
            "steps": self.steps_taken,
            "rescued": self.rescued_count,
            "remaining_targets": len(self.brain.targets),
            "total_reward": self.total_reward
        }

    def reset(self):
        self.worker.x, self.worker.y = 0, 0
        self.worker.wait_time = 0
        self.worker.on_fire = False
        self.worker.in_smoke = False
        self.worker.speed_factor = 1
        self.worker.vision_range = 999
        self.targets = []
        for x, row in enumerate(self.map_grid):
            for y, cell in enumerate(row):
                if cell == 4:
                    self.targets.append((x, y))
        self.brain.targets = self.targets[:]
        self.steps_taken = 0
        self.rescued_count = 0
        self.total_reward = 0
        self.done = False
        self.current_path = []

    def pretrain(self, episodes=50, max_steps_per_episode=200):
        for _ in range(episodes):
            self.reset()
            steps = 0
            while not self.done and steps < max_steps_per_episode:
                self.step()
                steps += 1