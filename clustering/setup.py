from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(ext_modules=cythonize('src/data_processing/DBSCAN_refactor_cy.pyx'),
      include_dirs=[numpy.get_include()])
