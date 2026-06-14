import json
import os

MAP_FOLDER = "Maps"

def load_map(map_filename):
    path = os.path.join(MAP_FOLDER, map_filename)
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading map: {e}")

    if not isinstance(data.get('width'), int) or data['width'] <= 0:
        raise ValueError("Invalid width")
    if not isinstance(data.get('height'), int) or data['height'] <= 0:
        raise ValueError("Invalid height")

    grid = data.get('grid')
    if not isinstance(grid, list) or len(grid) != data['height']:
        raise ValueError("Grid height mismatch")
    for row in grid:
        if not isinstance(row, list) or len(row) != data['width']:
            raise ValueError("Grid width mismatch")
        for cell in row:
            if not isinstance(cell, int) or cell < 0 or cell > 4:
                raise ValueError("Invalid cell value")

    return {
        "name": data.get("name", "unknown"),
        "width": data['width'],
        "height": data['height'],
        "grid": grid
    }

def get_cell(grid, x, y):
    if not grid:
        return -1
    if x < 0 or x >= len(grid):
        return -1
    row = grid[x]
    if y < 0 or y >= len(row):
        return -1
    return row[y]

def get_grid(map_data):
    return map_data["grid"]

def print_map(map_data):
    print(f"Map: {map_data['name']}")
    print(f"Width: {map_data['width']}, Height: {map_data['height']}")
    for row in map_data["grid"]:
        print(''.join(str(cell) for cell in row))