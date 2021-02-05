import math
import time
import multiprocessing

FLAG_ALL_DONE = b'WORK_FINISHED'
FLAG_WORKER_FINISHED_PROCESSING = b'WORKER_FINISHED_PROCESSING'


def check_prime(possible_primes_queue, definite_primes_queue):
    while True:
        n = possible_primes_queue.get()

        if n == FLAG_ALL_DONE:
            definite_primes_queue.put(FLAG_WORKER_FINISHED_PROCESSING)
            break
        else:
            if n % 2 == 0:
                continue
            for i in range(3, int(math.sqrt(n)) + 1, 2):
                if n % i == 0:
                    break
            else:
                definite_primes_queue.put(n)


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    possible_primes_queue = manager.Queue()
    definite_primes_queue = manager.Queue()

    N_WORKERS = 4

    pool = multiprocessing.Pool(processes=N_WORKERS)
    processes = []
    for _ in range(N_WORKERS):
        p = multiprocessing.Process(target=check_prime, args=(possible_primes_queue, definite_primes_queue))
        processes.append(p)
        p.start()

    t1 = time.time()
    number_range = range(10000_000_000, 10000_100_000)
    for possible_prime in number_range:
        possible_primes_queue.put(possible_prime)

    for n in range(N_WORKERS):
        possible_primes_queue.put(FLAG_ALL_DONE)

    primes = []
    processors_indicating_they_have_finished = 0
    while processors_indicating_they_have_finished < N_WORKERS:
        new_result = definite_primes_queue.get()
        if new_result == FLAG_WORKER_FINISHED_PROCESSING:
            processors_indicating_they_have_finished += 1
        else:
            primes.append(new_result)

    print("Took:", time.time() - t1)
    print(len(primes), primes[:10], primes[-10:])