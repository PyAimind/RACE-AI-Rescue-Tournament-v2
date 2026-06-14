import sys
from map_loader import load_map, get_grid
from worker import WorkerAgent

try:
    print("[1] Loading hospital map...")
    data = load_map("hospital.json")
    grid = get_grid(data)
    print("    OK.")

    print("[2] Creating worker at (0,0)...")
    w = WorkerAgent(0, 0, grid)
    print(f"    Pos: {w.get_position()}, Cell: {w.get_cell_type()}")

    print("[3] Moving RIGHT 3 times to hit rubble (cell=1) at (0,3)...")
    for i in range(3):
        old = w.get_position()
        w.move("RIGHT")
        new = w.get_position()
        print(f"    Step {i+1}: {old} -> {new}, cell={w.get_cell_type()}")
        if old == new:
            print("    OK: Worker blocked by rubble and stayed in place.")

    print("[4] Checking position is still before rubble...")
    assert w.get_position() == (0, 2), f"Expected (0,2) before rubble, got {w.get_position()}"
    print("    OK: Position correct, rubble not crossed.")

    print("[5] Moving DOWN (should work)...")
    w.move("DOWN")
    print(f"    Pos: {w.get_position()}, Cell: {w.get_cell_type()}")

    print("Test passed.")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)