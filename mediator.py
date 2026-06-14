from worker import WorkerAgent
from brain import BrainAgent

class MediatorAgent:
    def __init__(self, worker, brain):
        self.worker = worker
        self.brain = brain
        self.command_queue = []

    def execute_path(self, path):
        for direction in path:
            self.worker.move(direction)
            if self.worker.is_on_target():
                return True
            if self.worker.get_cell_type() == 2 and self.brain.is_dangerous(self.worker.get_position()):
                self.brain.learn_danger(self.worker.get_position())
        return self.worker.is_on_target()

    def step(self):
        if not self.command_queue:
            path = self.brain.replan(self.worker.get_position())
            if not path:
                return False
            self.command_queue = path[:]
        direction = self.command_queue.pop(0)
        self.worker.move(direction)
        if self.worker.is_on_target():
            return True
        if self.worker.get_cell_type() == 2:
            self.brain.learn_danger(self.worker.get_position())
            self.command_queue.clear()
        return False

    def emergency_direct_brain(self):
        path = self.brain.replan(self.worker.get_position())
        if path:
            self.worker.move(path[0])
            return self.worker.is_on_target()
        return False