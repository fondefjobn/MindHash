"""
For templating sensor usage
Not yet implemented.
"""
from abc import ABC, abstractmethod

from tools.structs import PopList


class Sensor(ABC):
    """
    Sensor template
    Any new sensor added to alternative inputs set must be
    subclassed by this class
    """

    @abstractmethod
    def read(self):
        """
        Function for any live reading
        Returns
        -------

        """
        return self.read.__name__

    @abstractmethod
    def convert(self):
        """
           Convert sensor output files from sensor native format to MatrixCloud
           for post-processing
           -------

           """
        return self.convert.__name__
