from threading import Event
from queue import Queue

from tools.pipes import RoutineSet, State
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

class Routines(RoutineSet):
    """
    Bundle for routines used to operate with StreamProcessor
    """

    def __init__(self):
        super().__init__()

    def id(self):
        return 'PROCESS_BUNDLE'

    @RoutineSet.poplist_loop(0, 'x')
    def list_processor(self, state: State, *args):  # abstract to methods
        """
        Routine to read from a parsed list of PopList elements
        and output to an allocated PopList
        Parameters
        ----------
        state
        args

        Returns
        -------

        """
        sp: StreamProcessor = StreamProcessor(args[0], args[1])
        out = args[0].get(state['x'], self.event)
        sp.read_stream(out)
        Routines.log.info(msg='ListProcessor: done')


class StreamProcessor:
    """
    StreamProcessor
    Executes data filtering and augmentation tasks
    Configuration file establishes the behavior of this class
    See Also config.yaml within package
    """
    config: dict = None
    idle: bool = False
    in_ls: PopList
    out_ls: PopList

    def __init__(self, in_ls: PopList, out_ls: PopList, cfg_path=None):
        self.in_ls = in_ls
        self.out_ls = out_ls
        # self._load_config(cfg_path)

    def _load_config(self, cfg_path):
        self.config = Fs.parse_yaml(cfg_path)

    def read_stream(self, mx):
        self.out_ls.add(Cloud3dUtils.to_pcdet(mx))
