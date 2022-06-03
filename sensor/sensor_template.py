"""
For templating sensor usage
Not yet implemented.
"""
import logging
from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import dataclass

from easydict import EasyDict

from tools.pipes.structures import RModule, DClass
from tools.structs import PopList
from utilities.utils import FileUtils


@dataclass
class SensorData(DClass):
    output: PopList
    config: str
    args: Namespace
    logger: logging.Logger
    __file__: str

    def __post_init__(self):
        self.check_missing(self)


class Sensor(ABC, RModule):
    """
    Sensor template
    Any new sensor added to alternative inputs set must be
    subclassed by this class
    Loads base config parameters
    """

    def __init__(self, sd: SensorData = None) -> None:
        super().__init__()
        self.output = sd.output
        self.logger = sd.logger
        self.load_config(__file__=sd.__file__, fname=sd.config)
        config = self.config
        args = sd.args
        self.N = config.N if args.n is None else args.n
        self.sample_rate = 0 if config.SAMPLE_RATE is None else config.SAMPLE_RATE
        self.BATCH_SIZE = 50 if config.BATCH_SIZE is None else config.BATCH_SIZE

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
