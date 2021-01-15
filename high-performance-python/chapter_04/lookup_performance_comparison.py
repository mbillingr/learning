import random
import string
from itertools import product
from timeit import timeit

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def build_list_phonebook(n):
    book = []
    for _ in range(n):
        name = ''.join(random.choices(string.ascii_uppercase, k=10))
        number = ''.join(random.choices(string.digits, k=10))
        book.append((name, number))
    return sorted(book)


def build_dict_phonebook(listbook):
    return {name: number for name, number in listbook}


def linear_lookup(who, l):
    return next(number for name, number in l if name == who)


def bisection_lookup(who, l, offset=0):
    if len(l) == 0: raise ValueError()

    p = len(l) // 2
    pivot_name, pivot_num = l[p]

    if pivot_name == who:
        return pivot_num

    elif pivot_name < who:
        return bisection_lookup(who, l[p + 1:], offset=offset + p + 1)

    elif pivot_name > who:
        return bisection_lookup(who, l[:p], offset=offset)


def dict_lookup(who, d):
    return d[who]


N_REPEAT = 15

t_lin = {}
t_bis = {}
t_dic = {}

N = np.round(np.logspace(0, 3, 15)).astype(int)
reps = range(N_REPEAT)

# distribute slow and fast work items, so that
# the timing estimate becomes more accurate
work_elements = list(product(N, reps))
random.shuffle(work_elements)

last_n = None
for n, _ in tqdm(work_elements):
    if n != last_n:
        l = build_list_phonebook(n)
        d = build_dict_phonebook(l)
        last_n = n

    name = random.choice(l)[0]

    t_lin.setdefault(n, []).append(timeit('linear_lookup(name, l)', globals=globals()))
    t_bis.setdefault(n, []).append(timeit('bisection_lookup(name, l)', globals=globals()))
    t_dic.setdefault(n, []).append(timeit('dict_lookup(name, d)', globals=globals()))


def draw(measurements, label):
    middle = np.array([np.mean(measurements[n]) for n in N])
    scatter = np.array([np.std(measurements[n]) for n in N])
    plt.loglog(N, [np.mean(measurements[n]) for n in N], label=label)
    plt.fill_between(N, middle - scatter, middle + scatter, alpha=0.3)


draw(t_lin, label='linear search')
draw(t_bis, label='bisection search')
draw(t_dic, label='dictionary search')
plt.show()
