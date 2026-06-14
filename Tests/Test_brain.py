import sys
from map_loader import load_map, get_grid
from brain import BrainAgent

try:
    data = load_map("hospital.json")
    grid = get_grid(data)
    targets = [(i,j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 4]
    brain = BrainAgent(grid, targets)
    
    print("Testing replan 5 times from (0,0):")
    paths = []
    for i in range(5):
        path = brain.replan((0, 0))
        first3 = tuple(path[:3]) if len(path) >= 3 else tuple(path)
        paths.append(first3)
        print(f"  {i+1}: {first3}")
    
    unique = len(set(paths))
    print(f"Unique paths: {unique}/5")
    if unique >= 2:
        print("OK: Path variety achieved.")
    else:
        print("FAIL: Still no variety.")
except Exception as e:
    print(f"FAIL: {e}")