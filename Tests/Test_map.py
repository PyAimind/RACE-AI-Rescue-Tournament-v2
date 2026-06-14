import sys
from map_loader import load_map, get_grid, print_map

try:
    data = load_map("hospital.json")
    print_map(data)
    grid = get_grid(data)
    assert len(grid) == data["height"]
    assert all(len(row) == data["width"] for row in grid)
    print("Test passed.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)