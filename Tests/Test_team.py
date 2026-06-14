import sys
from map_loader import load_map, get_grid
from worker import WorkerAgent
from brain import BrainAgent
from mediator import MediatorAgent

try:
    print("[1] Loading map...")
    data = load_map("hospital.json")
    grid = get_grid(data)
    print("    OK: Map loaded.")

    print("[2] Creating worker at (0,0)...")
    worker = WorkerAgent(0, 0, grid)
    print(f"    OK: Worker at {worker.get_position()}")

    print("[3] Finding targets on map...")
    targets = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 4:
                targets.append((i, j))
    print(f"    OK: Found {len(targets)} targets at {targets}")

    print("[4] Creating brain with targets...")
    brain = BrainAgent(grid, targets)
    print("    OK: Brain created.")

    print("[5] Creating mediator with worker and brain...")
    mediator = MediatorAgent(worker, brain)
    print("    OK: Mediator created.")

    print("[6] Brain finds path to nearest target...")
    path = brain.replan(worker.get_position())
    print(f"    Path found: {path[:5]}... (showing first 5 steps)")

    print("[7] Mediator executes steps until target reached...")
    steps = 0
    max_steps = 50
    while steps < max_steps:
        reached = mediator.step()
        steps += 1
        print(f"    Step {steps}: pos={worker.get_position()}, cell={worker.get_cell_type()}")
        if reached:
            print(f"    OK: Target reached in {steps} steps!")
            break
    else:
        print("    FAIL: Did not reach target within step limit.")

    assert worker.is_on_target(), "Worker should be on target"
    print("Test passed.")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)