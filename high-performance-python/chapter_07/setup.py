
# to build the extension module:
#   python setup.py build_ext --inplace

from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("cythonfn.pyx", compiler_directives={'language_level': '3'}))
