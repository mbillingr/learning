import mmh3
from blist import sortedset


class KMinValues:
    def __init__(self, num_hashes):
        self.num_hashes = num_hashes
        self.data = sortedset()

    def add(self, item):
        item_hash = mmh3.hash(item)
        self.data.add(item_hash)
        if len(self.data) > self.num_hashes:
            self.data.pop()

    def __len__(self):
        if len(self.data) <= 2:
            return 0
        length = (self.num_hashes - 1) * (2**32 - 1) / (self.data[-2] + 2**31 - 1)
        return int(length)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    N = 50000

    for s in [128, 512, 1024]:
        kmv = KMinValues(s)
        lengths = []
        for i in range(0, N):
            lengths.append(len(kmv))
            kmv.add(str(i))

        plt.plot(lengths)

    plt.plot([0, N], [0, N], 'k--')
    plt.show()
