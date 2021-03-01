import mmh3


class LL:
    def __init__(self, p):
        self.p = p
        self.num_registers = 2 ** p
        self.registers = [LogLogRegister() for _ in range(int(2 ** p))]
        self.alpha = 0.7213 / (1.0 + 1.079 / self.num_registers)

    def add(self, item):
        item_hash = mmh3.hash(str(item))
        register_index = item_hash & (self.num_registers - 1)
        register_hash = item_hash >> self.p
        self.registers[register_index]._add(register_hash)

    def __len__(self):
        register_sum = sum(h.counter for h in self.registers)
        length = (self.num_registers * self.alpha * 2 ** (register_sum / self.num_registers))
        return int(length)


class LogLogRegister:
    counter = 0

    def add(self, item):
        item_hash = mmh3.hash(str(item))
        return self._add(item_hash)

    def _add(self, item_hash):
        bit_index = trailing_zeros(item_hash)
        if bit_index > self.counter:
            self.counter = bit_index

    def __len__(self):
        return 2**self.counter


def trailing_zeros(number):
    """Returns the index of the first bit set to 1 from the right side of a 32-bit integer

    >>> trailing_zeros(0)
    32
    >>> trailing_zeros(0b1000)
    3
    >>> trailing_zeros(0b10000000)
    7
    """
    if not number:
        return 32
    index = 0
    while (number >> index) & 1 == 0:
        index += 1
    return index


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    N = 500000

    for s in [1, 2, 4]:
        ll = LL(s)
        lengths = []
        for i in range(0, N):
            lengths.append(len(ll))
            ll.add(str(i))

        plt.plot(lengths)

    plt.plot([0, N], [0, N], 'k--')
    plt.show()