import time

import numpy as np
from numpy import zeros, roll

grid_shape = (640, 640)


@profile  # for use with line profiler: kernprof -lv filename.py
def evolve(grid, dt, out, D=1.0):
    laplacian(grid, out)
    out *= D * dt
    out += grid


def laplacian(grid, out):
    np.copyto(out, grid)
    out *= -4
    out += roll(grid, +1, 0)
    out += roll(grid, -1, 0)
    out += roll(grid, +1, 1)
    out += roll(grid, -1, 1)


def run_experiment(num_iterations):
    # Initial conditions
    next_grid = zeros(grid_shape)
    grid = zeros(grid_shape)

    block_low = int(grid_shape[0] * 0.4)
    block_high = int(grid_shape[0] * 0.5)
    grid[block_low:block_high, block_low: block_high] = 0.005

    # Simulate
    start = time.time()
    for i in range(num_iterations):
        evolve(grid, 0.1, next_grid)
        grid, next_grid = next_grid, grid
    return time.time() - start


if __name__ == '__main__':
    run_experiment(100)
