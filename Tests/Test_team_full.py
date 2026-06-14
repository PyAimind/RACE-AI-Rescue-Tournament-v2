import sys
from map_loader import load_map, get_grid
from team import Team

try:
    print("[1] Loading map...")
    data = load_map("hospital.json")
    grid = get_grid(data)
    print("    OK: Map loaded.")

    print("[2] Creating team 'Blue' at (0,0)...")
    team = Team("Blue", (0, 0), grid)
    status = team.get_status()
    print(f"    OK: Team {status['name']} created. Remaining targets: {status['remaining_targets']}")

    print("[3] Running steps until all targets rescued...")
    max_steps = 100
    for i in range(max_steps):
        reached = team.step()
        pos = team.get_position()
        cell = grid[pos[0]][pos[1]]
        if reached:
            print(f"    Step {i+1}: pos={pos}, cell={cell} -> RESCUED! (total: {team.rescued})")
        if team.has_won():
            print(f"    OK: All targets rescued in {i+1} steps!")
            break
    else:
        print("    FAIL: Did not rescue all targets within step limit.")

    assert team.has_won(), "Team should have rescued all targets"
    final_status = team.get_status()
    print(f"[4] Final status: {final_status}")
    print("Test passed.")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)