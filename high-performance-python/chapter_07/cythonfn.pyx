from cython.parallel import prange
import cython
import numpy as np
cimport numpy as np

@cython.boundscheck(False)
def calculate_z(maxiter, double complex[:] zs, double complex[:] cs):
    """Calculate output list using Julia update rule"""
    cdef unsigned int i, n, length
    cdef double complex z, c
    cdef int[:] output = np.empty(len(zs), dtype=np.int32)
    length = len(zs)
    for i in range(length):
        z = zs[i]
        c = cs[i]
        output[i] = 0
        while output[i] < maxiter and (z.real**2 + z.imag**2) < 4:
            z = z * z + c
            output[i] += 1
    return output