from queue import Queue
from typing import List, Tuple

import numpy as np
from easydict import EasyDict
from numba import jit

from tools.pipes import RNode
from tools.pipes.structures import RModule
from tools.structs.custom_structs import PopList, MatrixCloud
from utilities.utils import FileUtils as Fs, \
    Cloud3dUtils, FileUtils

"""
@Module: Stream Processor
@Description: Provides functionalities for data filtering and augmentation tasks
@Author: Radu Rebeja
"""


class ConfigMap:
    """"""
    rate = 'sample_rate'
    q_size = 'queue_size'
    timer = 'timer'
    t_end = 'timer_stop'
    sl = 'local_saves'
    lp = 'local_path'
    live = 'livestream'


"""Aliases & Global values"""
################
Cm = ConfigMap
Q = Queue


################

class StreamProcessor(RModule):
    """
    StreamProcessor
    Executes data filtering and augmentation tasks
    Configuration file establishes the behavior of this class
    See Also config.yaml within package
    """

    c: dict = None

    idle: bool = False

    def __init__(self, cfg_path=None):  # def __init__(self, cfg_path=None): #
        super().__init__()
        self.load_config(__file__)
        print(self.config)

    def read_stream(self, mx: MatrixCloud):
        pcd = Cloud3dUtils.to_pcdet(mx)
        config = self.config
        param = config.STEPS.LIST[0].CONFIG
        pcd = pcd[((pcd[:, 0] > param.X[0]) &
                   (pcd[:, 0] < param.X[1]))
                  &
                  ((pcd[:, 1] > param.Y[0]) &
                   (pcd[:, 1] < param.Y[1]))
                  &
                  ((pcd[:, 2] > param.Z[0]) &
                   (pcd[:, 2] < param.Z[1]))
                  ]
        return pcd

    def fconfig(self):
        return "config.yaml"


class Routines(RNode):
    """
    StreamProcessor routine
    """
    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    @classmethod
    def script(cls, parser) -> bool:
        return True

    def __init__(self, state):
        super().__init__(state)

    sp: StreamProcessor = StreamProcessor()

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        """
        Routine to read from a parsed list of PopList elements
        and output to an allocated PopList
        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        self.state.logger.info(msg="Stream Processor started...")
        while not _input[0].full(self.ix):
            out = _input[0].qy(self.ix, self.event)
            output.append(self.sp.read_stream(out))
            self.ix += 1
        self.state.logger.info(msg="Stream Processor : DONE")

    def dependencies(self):
        from sensor.sensor_controller import Routines as Input
        return [Input]
