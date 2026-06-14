from map_loader import get_cell

class WorkerAgent:
    def __init__(self, start_x, start_y, map_grid):
        self.x = start_x
        self.y = start_y
        self.map_grid = map_grid
        self.speed_factor = 1
        self.wait_time = 0
        self.vision_range = 999
        self.on_fire = False
        self.in_smoke = False

    def move(self, direction, brain_allow=False):
        if self.wait_time > 0:
            self.wait_time -= 1
            return (self.x, self.y), "blocked"   # در حال مکث است و نمی‌تواند حرکت کند

        dirs = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
        if direction not in dirs:
            return (self.x, self.y), "blocked"
        dx, dy = dirs[direction]
        new_x, new_y = self.x + dx, self.y + dy
        cell = get_cell(self.map_grid, new_x, new_y)
        if cell == -1:
            return (self.x, self.y), "blocked"
        if cell == 2 and not brain_allow:
            return (self.x, self.y), "blocked"

        self.x, self.y = new_x, new_y

        event = "moved"
        if cell == 1:                     # آوار
            self.speed_factor = 0.5
            self.wait_time = 3            # مکث ۳ نوبتی (تازه اضافه شد)
            event = "hit_rubble"
        elif cell == 2:                   # آتش
            self.on_fire = True
            self.wait_time = 2
            event = "hit_fire"
            if brain_allow:
                self.x, self.y = 0, 0     # ریسپان به نقطه شروع
        elif cell == 3:                   # دود
            self.in_smoke = True
            self.vision_range = 1
            event = "moved"
        elif cell == 4:                   # هدف نجات
            event = "rescued"
        else:                             # مسیر آزاد
            self.speed_factor = 1
            self.wait_time = 0
            self.on_fire = False
            self.in_smoke = False
            self.vision_range = 999

        return (self.x, self.y), event

    def get_position(self):
        return (self.x, self.y)

    def get_cell_type(self):
        return get_cell(self.map_grid, self.x, self.y)

    def is_on_target(self):
        return self.get_cell_type() == 4

    def get_status(self):
        return {
            "speed_factor": self.speed_factor,
            "wait_time": self.wait_time,
            "on_fire": self.on_fire,
            "in_smoke": self.in_smoke,
            "vision_range": self.vision_range
        }