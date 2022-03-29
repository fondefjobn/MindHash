import numpy


def makearr():
    x = numpy.array([10,11,12])
    numpy.save('data.npy', x)

makearr()