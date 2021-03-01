import math
import random
import array


SMALLEST_UNSIGNED_INTEGER = 'B'


class MorrisCounter:
    """Approximate counter, stores exponent and counts approximately 2^exponent

    https://en.wikipedia.org/wiki/Approximate_counting_algorithm"""

    def __init__(self, type_code=SMALLEST_UNSIGNED_INTEGER, nbr_counters=1):
        self.exponents = array.array(type_code, [0] * nbr_counters)

    def __len__(self):
        return len(self.exponents)

    def add_counter(self):
        """Add a new zeroed counter"""
        self.exponents.append(0)

    def get(self, counter=0):
        """Calculate approximate value represented by counter"""
        return math.pow(2, self.exponents[counter])

    def add(self, counter=0):
        """Probabilistically add 1 to counter"""
        value = self.get(counter)
        probability = 1.0 / value
        if random.uniform(0, 1) < probability:
            self.exponents[counter] += 1


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    N = 10000

    mc = MorrisCounter()
    pcounts = []
    for _ in range(N):
        pcounts.append(mc.get())
        mc.add()
    plt.plot(pcounts)

    plt.plot([0, N], [0, N], 'k--')
    plt.show()



