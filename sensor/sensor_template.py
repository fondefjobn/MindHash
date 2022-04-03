"""
For templating sensor usage
Not yet implemented.
"""
from abc import ABC, abstractmethod


class Sensor(ABC):

    @abstractmethod
    def convert(self):
        pass
