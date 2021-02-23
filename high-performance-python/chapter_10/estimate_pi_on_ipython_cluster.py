import time

import ipyparallel as ipp
from ipyparallel import require


@require('random', 'os')
def estimate_nbr_points_in_quarter_circle(nbr_estimates):
    """Monte Carlo estimate of the number of points in a
    quarter circle using pure Python"""

    print(f"Executing estimate_nbr_points_in_quarter_circle({nbr_estimates}) on pid {os.getpid()}")

    nbr_trials_in_quarter_unit_cicle = 0
    for _ in range(int(nbr_estimates)):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        is_in_unit_cicle = x ** 2 + y ** 2 <= 1.0
        nbr_trials_in_quarter_unit_cicle += is_in_unit_cicle

    return nbr_trials_in_quarter_unit_cicle


if __name__ == "__main__":
    try:
        c = ipp.Client()
    except OSError as e:
        print("Hint: start a local cluster with e.g. `ipcluster start -n 8`")
        raise e
    nbr_engines = len(c.ids)
    print(f"We're using {nbr_engines} engines")
    nbr_samples_in_total = 1e8
    nbr_parallel_blocks = nbr_engines

    dview = c[:]

    nbr_samples_per_worker = nbr_samples_in_total / nbr_parallel_blocks
    t1 = time.time()
    nbr_in_quarter_unit_circles = dview.apply_sync(estimate_nbr_points_in_quarter_circle, nbr_samples_per_worker)
    print(f"Estimates: {nbr_in_quarter_unit_circles}")

    nbr_jobs = len(nbr_in_quarter_unit_circles)
    pi_estimate = sum(nbr_in_quarter_unit_circles) * 4 / nbr_samples_in_total
    print(f"Estimated pi: {pi_estimate}")
    print(f"Delta: {time.time() - t1}")
