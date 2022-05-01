from queue import Queue
from typing import List, Tuple

from numba import jit

from tools.pipes import RNode
from tools.structs.custom_structs import PopList
from utilities.utils import FileUtils as Fs, \
    Cloud3dUtils

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

class StreamProcessor:
    """
    StreamProcessor
    Executes data filtering and augmentation tasks
    Configuration file establishes the behavior of this class
    See Also config.yaml within package
    """
    config: dict = None
    idle: bool = False

    def __init__(self, cfg_path=None):  # def __init__(self, cfg_path=None): #
        pass

    def _load_config(self, cfg_path):
        self.config = Fs.parse_yaml(cfg_path)

    def read_stream(self, mx):
        return Cloud3dUtils.to_pcdet(mx)


class Routines(RNode):
    """
    StreamProcessor routine
    """
    @classmethod
    def script(cls, parser) -> bool:
        return False

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
        x = 0
        while not _input[0].full(x):
            out = _input[0].get(x, self.event)
            output.append(self.sp.read_stream(out))
            x += 1

    def dependencies(self):
        from sensor.sensor_controller import Routines as Input
        return [Input]
