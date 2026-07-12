import argparse
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument(
    "--scenario", "-s", help="3D scenario to be used",
    type=str, required=False, default="etoile"
)

args = parser.parse_args()

def assign_coordinates(num_tx, grid_size, initial_position_x, initial_position_y, spacing, z):
    positions = []

    for i in range(num_tx):
        row = i // grid_size
        col = i % grid_size

        x = initial_position_x + col * spacing
        y = initial_position_y + row * spacing

        positions.append([x, y, z])

    positions = np.array(positions)

    with open(f"path_gain_results/{args.scenario}_coordinates.csv", "w") as f:
        for coord_counter in range(len(positions)):
            f.write(f"{positions[coord_counter][0]},{positions[coord_counter][1]},{positions[coord_counter][2]},0,0\n")

if __name__ == "__main__":
    assign_coordinates(42, 7, -724, 786, 70, 17)