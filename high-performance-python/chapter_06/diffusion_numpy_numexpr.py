import time

import numpy as np
from numpy import zeros, roll
from numexpr import evaluate

grid_shape = (640, 640)


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


@profile  # for use with line profiler: kernprof -lv filename.py
def evolve(grid, dt, next_grid, D=1.0):
    laplacian(grid, next_grid)
    evaluate("next_grid * D * dt + grid", out=next_grid)


def laplacian(grid, out):
    np.copyto(out, grid)
    out *= -4
    roll_add(grid, +1, 0, out)
    roll_add(grid, -1, 0, out)
    roll_add(grid, +1, 1, out)
    roll_add(grid, -1, 1, out)


def roll_add(rollee, shift, axis, out):
    """
    Given a matrix, a rollee, and an output matrix, out, this function will perform the calculation:

        >>> out += np.roll(rollee, shift, axis=axis)

    This is done with the following assumptions:
      * rollee is 2D
      * shift will only ever be +1 or -1
      * axis will only ever be 0 or 1

    Using these assumptions, we are able to speed up this function by avoiding
    extra machinery that numpy uses to generalize the roll function and also
    by maxing this operation intrinsically in-place.
    """
    if shift == 1 and axis == 0:
        out[1:, :] += rollee[:-1, :]
        out[0, :] += rollee[-1, :]
    elif shift == -1 and axis == 0:
        out[:-1, :] += rollee[1:, :]
        out[-1, :] += rollee[0, :]
    elif shift == 1 and axis == 1:
        out[:, 1:] += rollee[:, :-1]
        out[:, 0] += rollee[:, -1]
    elif shift == -1 and axis == 1:
        out[:, :-1] += rollee[:, 1:]
        out[:, -1] += rollee[:, 0]


if __name__ == '__main__':
    run_experiment(1000)
