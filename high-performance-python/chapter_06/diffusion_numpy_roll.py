import time
from numpy import zeros, roll

grid_shape = (640, 640)


@profile  # for use with line profiler: kernprof -lv filename.py
def evolve(grid, dt, D=1.0):
    return grid * dt * D * laplacian(grid)


def laplacian(grid):
    return roll(grid, +1, 0) + roll(grid, -1, 0) + roll(grid, +1, 1) + roll(grid, -1, 1) - 4 * grid


def run_experiment(num_iterations):
    # Initial conditions
    xmax, ymax = grid_shape
    grid = zeros(grid_shape)

    block_low = int(grid_shape[0] * 0.4)
    block_high = int(grid_shape[0] * 0.5)
    grid[block_low:block_high, block_low: block_high] = 0.005

    # Simulate
    start = time.time()
    for i in range(num_iterations):
        grid = evolve(grid, 0.1)
    return time.time() - start


if __name__ == '__main__':
    run_experiment(100)
